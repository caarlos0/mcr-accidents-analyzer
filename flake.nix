{
  description = "Web scraper for opresente.com.br";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3;
        pythonWithPackages = python.withPackages (ps: with ps; [
          requests
          beautifulsoup4
          anthropic
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pythonWithPackages
          ];
          shellHook = ''
            echo "Web scraper development environment"
            echo "Python version: $(python --version)"
            echo "Available packages: requests, beautifulsoup4"
          '';
        };
      }
    );
}
