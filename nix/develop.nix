{ pkgs, versions }:
let
  python = pkgs.${versions.python};
  backend_deps = import ./targets/backend/deps { inherit pkgs versions; };
  base_pkgs = [
    pkgs.just
    pkgs.pre-commit
    pkgs.ruff
    pkgs.ruff-lsp
    pkgs.nodePackages.pyright
  ];
  dev_pylibs = ps: with ps; [
    pip
    mypy
    # pandas-stubs
    types-requests
    types-dateutil
    types-pytz
    black
  ];
in
{
  nopylibs = pkgs.mkShell {
    packages = base_pkgs ++ [
      (python.withPackages dev_pylibs)
    ];
  };
  pylibs = pkgs.mkShell {
    packages = base_pkgs ++ [
      (python.withPackages (ps:
        backend_deps.pylibs ++ (dev_pylibs ps)
      ))
    ];
  };
}
