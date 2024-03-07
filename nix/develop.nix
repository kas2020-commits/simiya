{pkgs}: let
  base_pkgs = [
    pkgs.just
    pkgs.pre-commit
  ];
in {
  default = pkgs.mkShell {
    packages = base_pkgs;
    nativeBuildInputs = with pkgs.ocamlPackages; [
      ocaml
      findlib
      utop
      dune_2
      ocaml-lsp
    ];
  };
}
