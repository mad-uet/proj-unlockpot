# PROTOTYPE: minh hoa quy trinh, khong tai lap du lieu hoac ket qua goc.
args <- commandArgs(trailingOnly = TRUE)
file_arg <- sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])
base_dir <- dirname(normalizePath(file_arg))
.libPaths(c(file.path(base_dir, ".library"), .libPaths()))
for (pkg in c("psych", "GPArotation", "lavaan", "plspm")) {
  if (!requireNamespace(pkg, quietly = TRUE)) stop("Missing ", pkg, "; run Rscript setup.R trong thu muc research/analysis")
}
out <- if (length(args)) args[1] else file.path(base_dir, "output")
dir.create(out, recursive = TRUE, showWarnings = FALSE)
out <- normalizePath(out)
meta <- read.csv(file.path(base_dir, "indicators.csv"), stringsAsFactors = FALSE)
audit <- read.csv(file.path(base_dir, "..", "notes", "indicator-audit.csv"))
expected <- audit$indicator[audit$source == "Appendix F, Table A4, p. 23"]
stopifnot(nrow(meta) == 49, !anyDuplicated(meta$indicator),
          identical(meta$indicator, expected))
groups <- unique(meta$group)
stopifnot(identical(as.integer(table(factor(meta$group, levels = groups))),
                    c(8L, 7L, 7L, 4L, 3L, 9L, 6L, 5L)))

seed <- 20261104L
RNGkind("Mersenne-Twister", "Inversion", "Rejection")
set.seed(seed)
n <- 829L
# Tao mot lan voi tham so co dinh, khong tim seed de khop bai bao.
common <- rnorm(n)
latent <- sqrt(0.30) * common + sqrt(0.70) * matrix(rnorm(n * 8), n, 8)
X <- sapply(seq_len(nrow(meta)), function(j) {
  g <- match(meta$group[j], groups)
  continuous <- 0.75 * latent[, g] + sqrt(1 - 0.75^2) * rnorm(n)
  as.integer(cut(continuous, c(-Inf, -1.2, -0.4, 0.4, 1.2, Inf), labels = FALSE))
})
colnames(X) <- meta$indicator
stopifnot(all(is.finite(X)), all(X >= 1 & X <= 5), all(X == trunc(X)))
# Chi lay so dem vai tro tu Bang 2, khong gan quan he vai tro voi diem.
role_levels <- c("Chu dau tu", "Giam sat", "Tong thau", "Thau phu", "Vat lieu", "Thiet bi")
role <- factor(sample(rep(role_levels, c(164, 132, 189, 149, 101, 94))), levels = role_levels)
write.csv(data.frame(id = seq_len(n), role = role, X, check.names = FALSE),
          file.path(out, "synthetic-829.csv"), row.names = FALSE, na = "")
# Vai tro la danh nghia. Ma hoa tham chieu: 1 intercept va 5 bien gia.
design <- model.matrix(~ role, contrasts.arg = list(role = contr.treatment(6)))
colnames(design) <- c("intercept", paste0("role_", 2:6))
write.csv(data.frame(id = seq_len(n), design), file.path(out, "role-design.csv"), row.names = FALSE)

# Khong dien bu, khong dao diem, chi tinh khi du k so nguyen hop le.
score_group <- function(values) {
  valid <- vapply(as.list(values), function(v) is.numeric(v) && length(v) == 1 &&
                    is.finite(v) && v == trunc(v) && v >= 1 && v <= 5, logical(1))
  if (!all(valid)) return(NA_real_)
  mean(unlist(values))
}
alpha <- function(m) {
  k <- ncol(m)
  k / (k - 1) * (1 - sum(apply(m, 2, var)) / var(rowSums(m)))
}
scores <- sapply(groups, function(g) apply(X[, meta$group == g, drop = FALSE], 1, score_group))
colnames(scores) <- groups
write.csv(data.frame(id = seq_len(n), scores), file.path(out, "group-scores.csv"), row.names = FALSE)
summary <- do.call(rbind, lapply(groups, function(g) {
  m <- X[, meta$group == g, drop = FALSE]
  data.frame(group = g, group_vi = meta$group_vi[match(g, meta$group)], k = ncol(m), n = n,
             mean = mean(scores[, g]), sd = sd(scores[, g]), median = median(scores[, g]),
             alpha_raw = alpha(m), mean_first_person = scores[1, g])
}))
write.csv(summary, file.path(out, "group-summary.csv"), row.names = FALSE)
citc <- do.call(rbind, lapply(groups, function(g) {
  m <- X[, meta$group == g, drop = FALSE]
  data.frame(group = g, indicator = colnames(m),
             citc = sapply(seq_len(ncol(m)), function(j) cor(m[, j], rowSums(m) - m[, j])),
             alpha_if_deleted = sapply(seq_len(ncol(m)), function(j) alpha(m[, -j, drop = FALSE])))
}))
write.csv(citc, file.path(out, "citc.csv"), row.names = FALSE)

# Pearson tren Likert la xap xi cua demo, khong phai tuong quan polychoric.
R <- cor(X)
inv <- solve(R)
partial <- -cov2cor(inv)
diag(partial) <- diag(R) <- 0
kmo <- sum(R^2) / (sum(R^2) + sum(partial^2))
correlation <- cor(X)
p <- ncol(X)
bartlett <- -(n - 1 - (2 * p + 5) / 6) * as.numeric(determinant(correlation, logarithm = TRUE)$modulus)
df <- p * (p - 1) / 2
pca <- prcomp(X, center = TRUE, scale. = TRUE)
eigenvalues <- pca$sdev^2
variance <- eigenvalues / sum(eigenvalues)
write.csv(data.frame(component = seq_len(p), eigenvalue = eigenvalues,
                     variance = variance, cumulative = cumsum(variance)),
          file.path(out, "pca-variance.csv"), row.names = FALSE)
write.csv(data.frame(indicator = meta$indicator, pca$rotation, check.names = FALSE),
          file.path(out, "pca-vectors.csv"), row.names = FALSE)
# Tai tuong quan bien-thanh phan, khac vector rieng.
loadings <- sweep(pca$rotation, 2, pca$sdev, "*")
write.csv(data.frame(indicator = meta$indicator, loadings, check.names = FALSE),
          file.path(out, "pca-loadings.csv"), row.names = FALSE)
write.csv(data.frame(n = n, p = p, kmo = kmo, bartlett_chisq = bartlett,
                     bartlett_df = df, bartlett_log_p = pchisq(bartlett, df, lower.tail = FALSE, log.p = TRUE),
                     kaiser_components = sum(eigenvalues > 1), first8_variance = sum(variance[1:8])),
          file.path(out, "diagnostics.csv"), row.names = FALSE)

# Cac tinh huong de nguoi hoc phan hoi, tach khoi mau phan tich day du.
cases <- list(du_8_cau = as.list(c(4, 4, 4, 4, 4, 4, 4, 4)),
              thieu_1_cau = as.list(c(NA, rep(4, 7))),
              trong_ca_nhom = as.list(rep(NA_real_, 8)),
              nhap_0 = as.list(c(0, rep(4, 7))),
              nhap_6 = as.list(c(6, rep(4, 7))),
              nhap_4_5 = as.list(c(4.5, rep(4, 7))),
              nhap_chu = c(list("abc"), as.list(rep(4, 7))))
write.csv(data.frame(scenario = names(cases),
                     score = vapply(cases, score_group, numeric(1))),
          file.path(out, "scoring-scenarios.csv"), row.names = FALSE, na = "")
svg(file.path(out, "pca-scree.svg"), width = 8, height = 4.5)
plot(seq_len(p), eigenvalues, type = "b", pch = 19,
     xlab = "Thành phần chính", ylab = "Trị riêng", main = "PCA trên dữ liệu tổng hợp")
abline(h = 1, lty = 2, col = "blue")
dev.off()
writeLines(c(paste("seed:", seed), "N: 829; p: 49; latent correlation: 0.30; loading: 0.75",
             "cut points: -1.2, -0.4, 0.4, 1.2; no simulated missingness in analysis sample",
             "Final PCA: Pearson, eigenvalue > 1 and direct oblimin; not common-factor EFA",
             "Preliminary: independent 438 x 52 Table 1 input, seed=20261105; screening flags only",
             "CFA WLSMV, CR, AVE, Pearson HTMT and conventional Mode A PLS with 1000 bootstrap executed",
             "No common-factor exploratory EFA, no original data replication; see extended-parameters.txt"),
           file.path(out, "parameters.txt"))
source(file.path(base_dir, "preliminary.R"))
run_preliminary(audit, out)
source(file.path(base_dir, "extended.R"))
models <- run_extended(X, meta, role, design, out)
capture.output(sessionInfo(), file = file.path(out, "sessionInfo.txt"))
status <- system2("python", c("-I", shQuote(file.path(base_dir, "build-assets.py")), shQuote(out)))
if (status != 0) stop("Khong tao duoc tai san prototype")
print(summary[, c("group", "k", "mean", "alpha_raw")], row.names = FALSE)
cat("KMO =", kmo, "; PCA eigenvalue > 1:", sum(eigenvalues > 1),
    "; variance first 8 =", sum(variance[1:8]), "\n")
cat("Output:", out, "\n")
