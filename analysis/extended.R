# PROTOTYPE. Explicit illustrative models, not the authors' unreleased specification.
run_extended <- function(X, meta, role, design, out) {
  for (pkg in c("psych", "GPArotation", "lavaan", "plspm")) {
    if (!requireNamespace(pkg, quietly = TRUE)) stop("Missing package ", pkg, "; run setup.R")
  }
  write_table <- function(x, name) write.csv(x, file.path(out, name), row.names = FALSE, na = "")
  groups <- unique(meta$group)
  warnings_seen <- character()
  capture_warning <- function(w) {
    warnings_seen <<- c(warnings_seen, conditionMessage(w))
    # The warning is recorded and also remains visible in the execution log.
  }
  withCallingHandlers({
    # Retain components by the same eigenvalue > 1 illustration as the base runner.
    n_components <- sum(eigen(cor(X), symmetric = TRUE, only.values = TRUE)$values > 1)
    rotated <- psych::principal(X, nfactors = n_components, rotate = "oblimin", scores = FALSE)
    write_table(data.frame(indicator = meta$indicator, unclass(rotated$loadings), check.names = FALSE),
                "pca-oblimin-pattern.csv")
    write_table(data.frame(indicator = meta$indicator, rotated$Structure, check.names = FALSE),
                "pca-oblimin-structure.csv")
    write_table(data.frame(component = rownames(rotated$Phi), rotated$Phi, check.names = FALSE),
                "pca-oblimin-phi.csv")
    write_table(data.frame(metric = rownames(rotated$Vaccounted), rotated$Vaccounted, check.names = FALSE),
                "pca-oblimin-variance.csv")
    saveRDS(rotated, file.path(out, "pca-oblimin.rds"))

    # Eight correlated common factors. All indicators ordinal, no cross-loadings,
    # no residual covariance, unit latent variances. Never modify after fit indices.
    safe_names <- make.names(meta$indicator, unique = TRUE)
    cfa_data <- as.data.frame(X)
    names(cfa_data) <- safe_names
    syntax <- paste(vapply(groups, function(g) {
      paste0("F", g, " =~ ", paste(safe_names[meta$group == g], collapse = " + "))
    }, character(1)), collapse = "\n")
    writeLines(syntax, file.path(out, "cfa-model.lav"))
    write_table(data.frame(indicator = meta$indicator, r_name = safe_names, group = meta$group), "cfa-name-map.csv")
    fit <- lavaan::cfa(syntax, data = cfa_data, ordered = safe_names,
                       estimator = "WLSMV", std.lv = TRUE, parameterization = "delta")
    saveRDS(fit, file.path(out, "cfa-fit.rds"))
    converged <- lavaan::lavInspect(fit, "converged")
    admissible <- lavaan::lavInspect(fit, "post.check")
    if (!converged || !admissible) stop("CFA did not converge or has an inadmissible solution; inspect saved fit")
    fit_measures <- lavaan::fitMeasures(fit)
    write_table(data.frame(metric = names(fit_measures), value = as.numeric(fit_measures)), "cfa-fit-measures.csv")
    standardized <- lavaan::standardizedSolution(fit)
    parameters <- lavaan::parameterEstimates(fit, standardized = TRUE)
    write_table(parameters, "cfa-parameters.csv")
    write_table(standardized, "cfa-standardized.csv")
    write_table(data.frame(factor = rownames(lavaan::lavInspect(fit, "cor.lv")),
                           lavaan::lavInspect(fit, "cor.lv"), check.names = FALSE), "cfa-factor-correlations.csv")
    reliability <- do.call(rbind, lapply(groups, function(g) {
      indicators <- safe_names[meta$group == g]
      loadings <- standardized$est.std[standardized$op == "=~" & standardized$lhs == paste0("F", g)]
      residuals <- standardized$est.std[standardized$op == "~~" & standardized$lhs == standardized$rhs &
                                         standardized$lhs %in% indicators]
      stopifnot(length(loadings) == length(indicators), length(residuals) == length(indicators), all(residuals >= 0))
      data.frame(group = g, k = length(indicators), min_loading = min(loadings), max_loading = max(loadings),
                 CR = sum(loadings)^2 / (sum(loadings)^2 + sum(residuals)),
                 AVE = sum(loadings^2) / (sum(loadings^2) + sum(residuals)))
    }))
    write_table(reliability, "cfa-cr-ave.csv")
    write_table(data.frame(converged = converged, admissible = admissible, n = nrow(X), p = ncol(X),
                           estimator_requested = "WLSMV", parameterization = "delta", ordered = TRUE,
                           std_lv = TRUE), "cfa-status.csv")

    # Original absolute-correlation HTMT, Pearson approximation on observed Likert.
    # This is separate from the ordinal WLSMV CFA and its latent correlations.
    R <- abs(cor(X))
    htmt <- diag(1, length(groups))
    dimnames(htmt) <- list(groups, groups)
    pairs <- list()
    for (i in seq_len(length(groups) - 1)) for (j in (i + 1):length(groups)) {
      a <- which(meta$group == groups[i]); b <- which(meta$group == groups[j])
      within_a <- R[a, a][upper.tri(R[a, a])]
      within_b <- R[b, b][upper.tri(R[b, b])]
      value <- mean(R[a, b]) / sqrt(mean(within_a) * mean(within_b))
      htmt[i, j] <- htmt[j, i] <- value
      pairs[[length(pairs) + 1]] <- data.frame(group_a = groups[i], group_b = groups[j],
                                             HTMT = value, below_085 = value < .85)
    }
    write_table(data.frame(group = groups, htmt, check.names = FALSE), "htmt-pearson.csv")
    write_table(do.call(rbind, pairs), "htmt-pairs.csv")

    # Conventional PLS-PM / Mode A. Five single-item dummy constructs predict
    # all eight capability composites. No capability-to-capability paths are invented.
    # Role dummy scores are standardized, so coefficients are not raw mean differences.
    role_names <- paste0("Role", 2:6)
    pls_names <- c(role_names, groups)
    inner <- matrix(0, length(pls_names), length(pls_names), dimnames = list(pls_names, pls_names))
    inner[groups, role_names] <- 1
    pls_data <- data.frame(design[, -1, drop = FALSE], X, check.names = FALSE)
    blocks <- c(lapply(seq_along(role_names), function(i) i),
                lapply(groups, function(g) which(meta$group == g) + length(role_names)))
    names(blocks) <- pls_names
    write_table(data.frame(construct = pls_names, inner, check.names = FALSE), "pls-inner-model.csv")
    write_table(data.frame(construct = rep(pls_names, lengths(blocks)),
                           indicator = names(pls_data)[unlist(blocks)], mode = "A"), "pls-blocks.csv")
    fit_pls <- function(d) plspm::plspm(d, inner, blocks, modes = rep("A", length(blocks)),
                                        scheme = "path", scaled = TRUE, tol = 1e-07,
                                        maxiter = 300, boot.val = FALSE, dataset = TRUE)
    pls <- fit_pls(pls_data)
    stopifnot(all(is.finite(pls$path_coefs)))
    positions <- which(inner == 1, arr.ind = TRUE)
    path_labels <- paste(colnames(inner)[positions[, 2]], "->", rownames(inner)[positions[, 1]])
    set.seed(20261106L)
    resamples <- replicate(1000, sample.int(nrow(pls_data), nrow(pls_data), replace = TRUE), simplify = FALSE)
    # Explicit bounded bootstrap: one fit per sampled dataset, no hidden redraws.
    # A failed convergence remains a recorded failed replicate rather than a retry.
    boot_one <- function(b) {
      messages <- character()
      tryCatch(withCallingHandlers({
        m <- fit_pls(pls_data[resamples[[b]], , drop = FALSE])
        values <- as.vector(m$path_coefs[inner == 1])
        stopifnot(length(values) == 40, all(is.finite(values)))
        list(values = values, iterations = as.integer(m$model$iter), warning = paste(messages, collapse = "; "), error = "")
      }, warning = function(w) { messages <<- c(messages, conditionMessage(w)); invokeRestart("muffleWarning") }),
      error = function(e) list(values = rep(NA_real_, 40), iterations = NA_integer_,
                              warning = paste(messages, collapse = "; "), error = conditionMessage(e)))
    }
    n_workers <- if (.Platform$OS.type == "windows") 1L else 2L
    draws <- vector("list", 1000)
    cat("Running 1000 bounded PLS bootstrap replicates with", n_workers, "workers...\n")
    for (start in seq(1L, 1000L, by = 100L)) {
      ids <- start:min(start + 99L, 1000L)
      draws[ids] <- parallel::mclapply(ids, boot_one, mc.cores = n_workers, mc.set.seed = FALSE)
      cat("Bootstrap attempted:", max(ids), "/ 1000\n")
    }
    boot_values <- do.call(rbind, lapply(draws, `[[`, "values"))
    colnames(boot_values) <- path_labels
    ok <- apply(boot_values, 1, function(x) all(is.finite(x)))
    write_table(data.frame(replicate = 1:1000, converged = ok,
                           iterations = vapply(draws, function(x) x$iterations, integer(1)),
                           warning = vapply(draws, `[[`, character(1), "warning"),
                           error = vapply(draws, `[[`, character(1), "error")), "pls-bootstrap-status.csv")
    write_table(data.frame(replicate = 1:1000, boot_values, check.names = FALSE), "pls-bootstrap-draws.csv")
    write_table(data.frame(attempted = 1000, successful = sum(ok), failed = sum(!ok),
                           workers = n_workers, seed = 20261106), "pls-bootstrap-counts.csv")
    if (sum(ok) < 2) stop("Insufficient converged bootstrap samples; inspect status file")
    boot <- data.frame(Original = as.vector(pls$path_coefs[inner == 1]),
                       Mean.Boot = colMeans(boot_values[ok, , drop = FALSE]),
                       Std.Error = apply(boot_values[ok, , drop = FALSE], 2, sd),
                       perc.025 = apply(boot_values[ok, , drop = FALSE], 2, quantile, probs = .025),
                       perc.975 = apply(boot_values[ok, , drop = FALSE], 2, quantile, probs = .975),
                       row.names = path_labels, check.names = FALSE)
    pls$boot <- list(paths = boot)
    saveRDS(pls, file.path(out, "pls-fit.rds"))
    stopifnot(nrow(pls$boot$paths) == 40)
    if (any(!ok)) warning(sum(!ok), " bootstrap samples failed. Intervals use successful samples only; see status/counts.")
    write_table(data.frame(construct = rownames(pls$path_coefs), pls$path_coefs, check.names = FALSE), "pls-paths.csv")
    write_table(data.frame(path = rownames(pls$boot$paths), pls$boot$paths, check.names = FALSE), "pls-bootstrap-paths.csv")
    write_table(pls$outer_model, "pls-outer-model.csv")
    write_table(data.frame(construct = rownames(pls$inner_summary), pls$inner_summary, check.names = FALSE), "pls-inner-summary.csv")
    write_table(data.frame(construct = rownames(pls$unidim), pls$unidim, check.names = FALSE), "pls-unidimensionality.csv")
    capture.output(summary(pls), file = file.path(out, "pls-summary.txt"))
    capture.output(summary(fit, fit.measures = TRUE, standardized = TRUE), file = file.path(out, "cfa-summary.txt"))
    write_table(data.frame(package = c("psych", "GPArotation", "lavaan", "plspm"),
                           version = vapply(c("psych", "GPArotation", "lavaan", "plspm"), function(p) as.character(utils::packageVersion(p)), character(1))),
                "package-versions.csv")
    writeLines(c("PCA Pearson, retain eigenvalue > 1, direct oblimin via GPArotation default gamma=0.",
                 "CFA: eight correlated factors, all 49 indicators ordinal, WLSMV, delta, std.lv=TRUE.",
                 "CFA CR and AVE use fully standardized loadings and residuals of latent responses.",
                 "HTMT: arithmetic means of absolute Pearson correlations; descriptive point estimates, no HTMT bootstrap.",
                 "PLS: traditional Mode A, path weighting, scaled=TRUE, tol=1e-7, maxiter=300.",
                 "PLS: five single-indicator role dummies -> all eight composites, no other predictors.",
                 "PLS bootstrap: 1000 pre-generated case resamples, seed=20261106, empirical 2.5/97.5 percentile intervals; at most two workers, no redraws. See status/counts for convergence.",
                 "PLS is not PLSc or the same estimator/model as ordinal CFA; no causal interpretation.",
                 "No project type / years predictors or tuning for original article results."), file.path(out, "extended-parameters.txt"))
    writeLines(unique(warnings_seen), file.path(out, "extended-warnings.txt"))
    cat("CFA converged:", converged, "; scaled CFI:", fit_measures["cfi.scaled"],
        "; scaled RMSEA:", fit_measures["rmsea.scaled"], "; max HTMT:", max(htmt[upper.tri(htmt)]), "\n")
  }, warning = capture_warning)
  invisible(list(cfa = fit, pls = pls))
}
