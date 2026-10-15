# Install public CRAN dependencies into an isolated local library of the research package.
# The library stays inside research/analysis/.library so the package is self-contained.
file_arg <- sub("^--file=", "", grep("^--file=", commandArgs(), value = TRUE)[1])
script_dir <- dirname(normalizePath(if (nzchar(file_arg)) file_arg else getwd()))
lib <- file.path(script_dir, ".library")
dir.create(lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(lib, .libPaths()))
packages <- c("psych", "GPArotation", "lavaan", "plspm")
missing <- packages[!vapply(packages, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) install.packages(missing, lib = lib, repos = "https://cloud.r-project.org", Ncpus = 2)
stopifnot(all(vapply(packages, requireNamespace, logical(1), quietly = TRUE)))
print(installed.packages(lib.loc = lib)[, c("Package", "Version")])
