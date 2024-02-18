{ pkgs, versions }:
let
  pyPackages = pkgs."${versions.python}Packages";
  pylibs = with pyPackages; [
    lark
    rich
    typer
    colorama
    networkx
    numpy
    scipy
    matplotlib
    pandas
  ];
  other_pkgs = [ ];
in
{
  inherit pylibs other_pkgs;
  native = [ pyPackages.flit-core ];
  propagate = pylibs ++ other_pkgs;
}
