# PROTOTYPE. Separate preliminary-stage input, not the 829-row final input.
run_preliminary <- function(audit, out) {
  if (!requireNamespace("psych", quietly = TRUE)) stop("Missing psych; run setup.R")
  source_rows <- audit[audit$source == "Table 1, pp. 6-7", , drop = FALSE]
  stopifnot(nrow(source_rows) == 52, !anyDuplicated(source_rows$indicator))
  groups <- unique(source_rows$group)
  expected_counts <- c(Bus = 8L, Fin = 7L, HR = 7L, LI = 6L,
                       Mkg = 4L, OM = 9L, PM = 6L, Proc = 5L)
  stopifnot(identical(as.integer(table(factor(source_rows$group, levels = groups))),
                      unname(expected_counts[groups])))
  n <- 438L
  seed <- 20261105L
  RNGkind("Mersenne-Twister", "Inversion", "Rejection")
  set.seed(seed)
  common <- rnorm(n)
  latent <- sqrt(0.30) * common + sqrt(0.70) * matrix(rnorm(n * length(groups)), n, length(groups))
  X <- sapply(seq_len(nrow(source_rows)), function(j) {
    g <- match(source_rows$group[j], groups)
    z <- 0.75 * latent[, g] + sqrt(1 - 0.75^2) * rnorm(n)
    as.integer(cut(z, c(-Inf, -1.2, -0.4, 0.4, 1.2, Inf), labels = FALSE))
  })
  colnames(X) <- source_rows$indicator
  stopifnot(all(is.finite(X)), all(X >= 1 & X <= 5), all(X == trunc(X)))
  role_levels <- c("Chu dau tu", "Giam sat", "Tong thau", "Thau phu", "Vat lieu", "Thiet bi")
  role <- factor(sample(rep(role_levels, c(19, 38, 103, 133, 71, 74))), levels = role_levels)
  write.csv(data.frame(id = seq_len(n), role = role, X, check.names = FALSE),
            file.path(out, "preliminary-438.csv"), row.names = FALSE, na = "")
  write.csv(data.frame(id = seq_len(n), model.matrix(~ role, contrasts.arg = list(role = contr.treatment(6)))[, -1, drop = FALSE]),
            file.path(out, "preliminary-role-design.csv"), row.names = FALSE)
  alpha <- function(m) {
    k <- ncol(m)
    if (k < 2) return(NA_real_)
    k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
  }
  metrics <- do.call(rbind, lapply(groups, function(g) {
    m <- X[, source_rows$group == g, drop = FALSE]
    before <- alpha(m)
    data.frame(group = g, n_indicators = ncol(m), alpha_before = before,
               mean = mean(m), sd = sd(as.vector(m)))
  }))
  screening <- do.call(rbind, lapply(groups, function(g) {
    m <- X[, source_rows$group == g, drop = FALSE]
    before <- alpha(m)
    data.frame(group = g, indicator = colnames(m),
               citc = vapply(seq_len(ncol(m)), function(j) cor(m[, j], rowSums(m) - m[, j]), numeric(1)),
               alpha_before = before,
               alpha_if_deleted = vapply(seq_len(ncol(m)), function(j) alpha(m[, -j, drop = FALSE]), numeric(1)))
  }))
  screening$review_flag <- screening$citc < 0.50 & screening$alpha_if_deleted > screening$alpha_before + 1e-6
  write.csv(screening, file.path(out, "preliminary-screening.csv"), row.names = FALSE, na = "")
  write.csv(metrics, file.path(out, "preliminary-group-summary.csv"), row.names = FALSE, na = "")
  authored_removed <- c("Cap-LI_1", "Cap-LI_4", "Cap-Mkg_3")
  sensitivity <- do.call(rbind, lapply(authored_removed, function(ind) {
    g <- source_rows$group[match(ind, source_rows$indicator)]
    m <- X[, source_rows$group == g, drop = FALSE]
    data.frame(indicator = ind, group = g, alpha_before = alpha(m),
               alpha_after_authored_list = alpha(m[, !colnames(m) %in% authored_removed, drop = FALSE]),
               simulated_citc = screening$citc[screening$indicator == ind])
  }))
  sensitivity$meaning <- "Danh muc do bai cong bo; khong phai quyet dinh loc tu du lieu tong hop"
  write.csv(sensitivity, file.path(out, "preliminary-authored-removals.csv"), row.names = FALSE, na = "")
  # Labels only for the three disputed indicators, from the extracted paper text.
  labels <- data.frame(indicator = authored_removed,
                       group = c("LI", "LI", "Mkg"),
                       label_en = c("Technical exchanges with external parties",
                                    "Internal learning mechanisms",
                                    "Joined a professional association"),
                       label_vi = c("Trao đổi kỹ thuật với các bên bên ngoài", "Cơ chế học hỏi nội bộ", "Tham gia hiệp hội nghề nghiệp"),
                       source = "Table 1, pp. 6-7 / article-extracted.txt")
  write.csv(labels, file.path(out, "preliminary-authored-removal-labels.csv"), row.names = FALSE)
  # The preliminary-stage oblimin is separate from final-stage oblimin.
  eigenvalues <- eigen(cor(X), symmetric = TRUE, only.values = TRUE)$values
  n_components <- sum(eigenvalues > 1)
  write.csv(data.frame(n = n, p = ncol(X), kaiser_components = n_components,
                       retained_variance = sum(eigenvalues[seq_len(n_components)]) / sum(eigenvalues),
                       review_flags = sum(screening$review_flag)),
            file.path(out, "preliminary-diagnostics.csv"), row.names = FALSE)
  write.csv(source_rows, file.path(out, "preliminary-indicators.csv"), row.names = FALSE)
  rotated <- psych::principal(X, nfactors = n_components, rotate = "oblimin", scores = FALSE)
  write.csv(data.frame(indicator = source_rows$indicator, unclass(rotated$loadings), check.names = FALSE),
            file.path(out, "preliminary-pca-oblimin-pattern.csv"), row.names = FALSE)
  write.csv(data.frame(indicator = source_rows$indicator, rotated$Structure, check.names = FALSE),
            file.path(out, "preliminary-pca-oblimin-structure.csv"), row.names = FALSE)
  write.csv(data.frame(component = rownames(rotated$Phi), rotated$Phi, check.names = FALSE),
            file.path(out, "preliminary-pca-oblimin-phi.csv"), row.names = FALSE)
  write.csv(data.frame(metric = rownames(rotated$Vaccounted), rotated$Vaccounted, check.names = FALSE),
            file.path(out, "preliminary-pca-oblimin-variance.csv"), row.names = FALSE)
  saveRDS(rotated, file.path(out, "preliminary-pca-oblimin.rds"))
  writeLines(c(paste("seed:", seed), "N: 438; source: Table 1 pp. 6-7; p: 52",
               "latent correlation: 0.30; loading: 0.75; cut points: -1.2, -0.4, 0.4, 1.2",
               "screening flag: CITC < 0.50 AND alpha_if_deleted > alpha_before + 1e-6",
               "flags are review signals only; no iterative deletion; final input remains 49 Appendix F indicators",
               paste("PCA direct oblimin components retained:", n_components)),
             file.path(out, "preliminary-parameters.txt"))
  invisible(list(data = X, screening = screening, pca = rotated))
}
