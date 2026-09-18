{
  description = "otoDB dev";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
      ];

      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f nixpkgs.legacyPackages.${system});
    in
    {
      devShells = forAllSystems (
        pkgs:
        let
          inherit (pkgs) lib stdenv;

          isLinux = stdenv.hostPlatform.isLinux;

          python = pkgs.python314;

          libraryPath = lib.makeLibraryPath [
            stdenv.cc.cc.lib
            pkgs.zlib
          ];
        in
        {
          default = pkgs.mkShell {
            name = "otodb";

            packages = [
              python
              pkgs.uv

              pkgs.bun
              pkgs.nodejs

              pkgs.postgresql_17

              # yt-dlp JS runtime
              pkgs.deno

              pkgs.docker-client
              pkgs.docker-compose

              pkgs.jq
              pkgs.git
            ];

            env = {
              UV_PYTHON_DOWNLOADS = "never";
              UV_PYTHON = python.interpreter;
            }
            // lib.optionalAttrs isLinux {
              LD_LIBRARY_PATH = libraryPath;
            };
          };
        }
      );
    };
}
