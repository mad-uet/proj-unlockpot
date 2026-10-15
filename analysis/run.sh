#!/usr/bin/env bash
# Bound BLAS threads before R loads; at most two bootstrap workers are used.
# Standalone entry point of the research analysis package (research/analysis).
set -euo pipefail
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
analysis_script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec Rscript "$analysis_script_dir/prototype.R" "$@"
