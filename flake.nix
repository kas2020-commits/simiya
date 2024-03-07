{
  description = "Simiya";

  inputs = {
    # nixpkgs = {
    #   url = "github:nixos/nixpkgs/nixos-23.11";
    # };

    nixpkgs-unstable = {
      url = "github:nixos/nixpkgs/nixos-unstable";
    };

    flake-parts = {
      url = "github:hercules-ci/flake-parts";
      inputs.nixpkgs-lib.follows = "nixpkgs-unstable";
    };
  };

  outputs = inputs @ {
    self,
    nixpkgs,
    flake-parts,
    ...
  }: let
    repo = import ./nix;
  in
    flake-parts.lib.mkFlake {inherit inputs;} {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];

      imports = [];

      perSystem = {
        pkgs,
        system,
        ...
      }: let
        shells = repo.devShells {inherit pkgs;};
      in {
        formatter = pkgs.alejandra;
        devShells = {
          inherit (shells) default;
        };
      };
    };
}
