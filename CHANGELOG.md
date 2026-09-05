# Changelog

## [1.2.1](https://github.com/tinogo/uc-intg-awol-valerion/compare/v1.2.0...v1.2.1) (2026-09-05)


### Bug Fixes

* Fix the run script entry point ([3c2acfe](https://github.com/tinogo/uc-intg-awol-valerion/commit/3c2acfecddcde5bb80d32afe9f64ebfb598f35e8))


### Miscellaneous

* **ci-cd:** require the pyinstaller package directly ([d1f740e](https://github.com/tinogo/uc-intg-awol-valerion/commit/d1f740e676c7b853771c969ce179b95880721693))
* **ci-cd:** update the setup-uv actions ([6d443e7](https://github.com/tinogo/uc-intg-awol-valerion/commit/6d443e7b839ffed26505c3352e0ca8adf844147b))
* **deps:** Update the dependencies ([325b3dc](https://github.com/tinogo/uc-intg-awol-valerion/commit/325b3dcbb99bd87fa2bfd5439c39b4f195ab431a))

## [1.2.0](https://github.com/tinogo/uc-intg-awol-valerion/compare/v1.1.1...v1.2.0) (2026-08-29)


### Features

* batch some query commands to reduce the latency ([da4b6b2](https://github.com/tinogo/uc-intg-awol-valerion/commit/da4b6b2032f3a1e1b161065105f414786a4a0f95))

## [1.1.1](https://github.com/tinogo/uc-intg-awol-valerion/compare/v1.1.0...v1.1.1) (2026-08-29)


### Bug Fixes

* correctly handle the available gamma and dynamic tone mapping select options ([72f3499](https://github.com/tinogo/uc-intg-awol-valerion/commit/72f34994804a6d7c432150cf7d85d1b72d18d23a))

## [1.1.0](https://github.com/tinogo/uc-intg-awol-valerion/compare/v1.0.2...v1.1.0) (2026-08-29)


### Features

* Pretty print the signal info ([b980d08](https://github.com/tinogo/uc-intg-awol-valerion/commit/b980d087b239ecd12960277fc51968f7ea94a463))


### Bug Fixes

* **ci-cd:** Revert the mutable releases as release-please seems to have a bug with draft releases ([bff99ee](https://github.com/tinogo/uc-intg-awol-valerion/commit/bff99ee1a4b6cb6abeb488c5c2548266fd754401))
* Do not allow changing the gamma value for HDR signals ([4805a51](https://github.com/tinogo/uc-intg-awol-valerion/commit/4805a51ce96f2ef959a18e859bae570ba20a98cb))
* harden against some possible errors ([f0f083e](https://github.com/tinogo/uc-intg-awol-valerion/commit/f0f083ee03a8f658a4e702a5953c7d2482d793ce))


### Miscellaneous

* Make the Fan Speed and Temperature sensor values a bit more compact ([e285479](https://github.com/tinogo/uc-intg-awol-valerion/commit/e285479890e3a06b8357bfe6bbabc9c3326f128d))

## [1.0.2](https://github.com/tinogo/uc-intg-awol-valerion/compare/v1.0.1...v1.0.2) (2026-08-29)


### Documentation

* add an AGENTS.md file ([6be1719](https://github.com/tinogo/uc-intg-awol-valerion/commit/6be17195e6a63f145a7bf0d83f7caff41be173c5))


### Miscellaneous

* **deps:** Update the dependencies ([2e3f4e3](https://github.com/tinogo/uc-intg-awol-valerion/commit/2e3f4e3c8191f6a2dff93f4fb7cb8af57e7400c2))
* update the uv version to 0.12.7 ([6e02ea9](https://github.com/tinogo/uc-intg-awol-valerion/commit/6e02ea99fce07e42d4bd58733c7448e9cbf5be9a))

## [1.0.1](https://github.com/tinogo/uc-intg-awol-valerion/compare/v1.0.0...v1.0.1) (2026-08-28)


### Bug Fixes

* let the integration setup fail when the authentication fails ([a833ca7](https://github.com/tinogo/uc-intg-awol-valerion/commit/a833ca72c77a1fd1de75f25f9db36d84015d5da5))


### Miscellaneous

* Enforce immutable releases ([b35ac20](https://github.com/tinogo/uc-intg-awol-valerion/commit/b35ac20e7ae63ad283153b8cdc1f9ea2a8751757))

## [1.0.0](https://github.com/tinogo/uc-intg-awol-valerion/compare/v0.6.0...v1.0.0) (2026-08-28)


### Miscellaneous

* **deps:** update the ucapi-framework ([112c851](https://github.com/tinogo/uc-intg-awol-valerion/commit/112c851cb77b13eb386b0b826423be9d7e0ccc28))
* **docs:** document on how to update a single package ([8d81c05](https://github.com/tinogo/uc-intg-awol-valerion/commit/8d81c05c1ea4be3bbca64a7142f265897350d560))
* move some code around ([e39c7b9](https://github.com/tinogo/uc-intg-awol-valerion/commit/e39c7b9d7bdfbb977b8626e3acc219f1af4b05dc))
* reduce the code duplication in the Select entity ([be6ca4c](https://github.com/tinogo/uc-intg-awol-valerion/commit/be6ca4cb4e6a6326d7dafd7e5f3f067d57aa65a0))
* reduce the code duplication in the Sensor entity ([657db7b](https://github.com/tinogo/uc-intg-awol-valerion/commit/657db7bc522d90cd179d3908bcf4283fe4bc8057))
* release 1.0.0 ([10ac17a](https://github.com/tinogo/uc-intg-awol-valerion/commit/10ac17ac52eef858db0b651f312c3b649d204646))
* treat every entity type to be self-contained ([b7a3518](https://github.com/tinogo/uc-intg-awol-valerion/commit/b7a351818480732477a8d12172857c5e0e8d95cc))

## [0.6.0](https://github.com/tinogo/uc-intg-awol-valerion/compare/v0.5.1...v0.6.0) (2026-08-28)


### Features

* add the Laser luminance select entity ([9a3f8ca](https://github.com/tinogo/uc-intg-awol-valerion/commit/9a3f8ca084a3b0f0ab519ebfbfaf6332bc7b8166))
* fetch the picture mode list dynamically ([bf4400c](https://github.com/tinogo/uc-intg-awol-valerion/commit/bf4400c738dbc4f62cc8f28b9cab953afa55c765))


### Documentation

* update the readme ([6866202](https://github.com/tinogo/uc-intg-awol-valerion/commit/6866202edbb0d53779fdf8f262d53c0b877516f1))


### Miscellaneous

* poll every 5 seconds instead of 30 seconds ([c480ff7](https://github.com/tinogo/uc-intg-awol-valerion/commit/c480ff7f4047578817a17521e0cc006247f247bf))

## [0.5.1](https://github.com/tinogo/uc-intg-awol-valerion/compare/v0.5.0...v0.5.1) (2026-08-27)


### Bug Fixes

* **#11:** fix the authentication ([8e5df89](https://github.com/tinogo/uc-intg-awol-valerion/commit/8e5df896ce8e55a3a387be30f763980c1b90186b)), closes [#11](https://github.com/tinogo/uc-intg-awol-valerion/issues/11)

## [0.5.0](https://github.com/tinogo/uc-intg-awol-valerion/compare/v0.4.0...v0.5.0) (2026-08-16)


### Features

* improve the visuals of the fan speed sensor ([73dbc93](https://github.com/tinogo/uc-intg-awol-valerion/commit/73dbc93a229922370541da325ebcdc3deae842ca))
* improve the visuals of the temperature sensor ([8ebb8b4](https://github.com/tinogo/uc-intg-awol-valerion/commit/8ebb8b43ff4e5fd8510a641dc3e30ff042d12f0b))
* refresh the device state after sending a command ([a82ae40](https://github.com/tinogo/uc-intg-awol-valerion/commit/a82ae40887d5740ba77808b1010b39b5cf436fbd))


### Bug Fixes

* fix changing the Select entity options ([45ed99c](https://github.com/tinogo/uc-intg-awol-valerion/commit/45ed99cf05bc19a7e326e39376f2baebee6c0c33))

## [0.4.0](https://github.com/tinogo/uc-intg-awol-valerion/compare/v0.3.0...v0.4.0) (2026-08-16)


### Features

* Add select entity support ([#14](https://github.com/tinogo/uc-intg-awol-valerion/issues/14)) ([bbb4092](https://github.com/tinogo/uc-intg-awol-valerion/commit/bbb4092e15e167fefba8de6ccefaf983ae44f280))


### Documentation

* extend the README with the supported Select Entities ([eb5c24b](https://github.com/tinogo/uc-intg-awol-valerion/commit/eb5c24bf7730699d67e1921e272d217663cb8f8e))

## [0.3.0](https://github.com/tinogo/uc-intg-awol-valerion/compare/v0.2.0...v0.3.0) (2026-08-16)


### Features

* **#10:** add support for various sensors ([daa7889](https://github.com/tinogo/uc-intg-awol-valerion/commit/daa7889edd5700cbec9377eb765cd95c1fca65ff))


### Bug Fixes

* Valerion projectors only allow muting the audio, but not the video output ([15c150d](https://github.com/tinogo/uc-intg-awol-valerion/commit/15c150d6b7870fe445357a066728d9ac2589344a))


### Documentation

* add an important note to let the authentication disabled for the AWOL Link protocol (for now) ([56049e3](https://github.com/tinogo/uc-intg-awol-valerion/commit/56049e37854f73960fa0a07f7344b60cbe8a6de6))

## [0.2.0](https://github.com/tinogo/uc-intg-awol-valerion/compare/v0.1.0...v0.2.0) (2026-08-15)


### Features

* **#9:** add a remote entity ([76a610b](https://github.com/tinogo/uc-intg-awol-valerion/commit/76a610bab3dd761af00239fc6bc3d917eed9738c))
* add simple commands ([710e454](https://github.com/tinogo/uc-intg-awol-valerion/commit/710e4544e4782c1d3fa0ad69ec44dc3776ebb861))


### Bug Fixes

* fix muting/unmuting ([83b57fd](https://github.com/tinogo/uc-intg-awol-valerion/commit/83b57fd0c9cd3a79f5a771c74fc5310cb9a6e0d7))


### Documentation

* **#9:** mention the remote entity in the readme ([f8abd04](https://github.com/tinogo/uc-intg-awol-valerion/commit/f8abd04d130aa4c4539c2344e68c26e8c963bc8e))
* fix a typo ([e8ae633](https://github.com/tinogo/uc-intg-awol-valerion/commit/e8ae633a0c55900ce7f44b33e1aa64fdfb1d5495))

## 0.1.0 (2026-08-15)


### Features

* add direct volume management + satisfy the linters ([0786359](https://github.com/tinogo/uc-intg-awol-valerion/commit/078635986b839c0725e871e0dd6e3e0df9f5e3d9))
* add support for the DPAD and basic volume management ([a05a3a5](https://github.com/tinogo/uc-intg-awol-valerion/commit/a05a3a5b904d79f05bc2cbce5e7863359fbf50e7))
* implement source switching in the media player ([5b3b8e4](https://github.com/tinogo/uc-intg-awol-valerion/commit/5b3b8e4a421202596c9fdc432a0133fbbf128686))


### Documentation

* update the readme ([5d8925e](https://github.com/tinogo/uc-intg-awol-valerion/commit/5d8925e332cdfb958348c32d7d37a62267712af9))


### Miscellaneous

* Initial commit ([3f65dd9](https://github.com/tinogo/uc-intg-awol-valerion/commit/3f65dd9521e8a08ad48ba4c8ed6cf71cd3938f0b))
* remove the unsupported "get errors"-query ([7d32400](https://github.com/tinogo/uc-intg-awol-valerion/commit/7d324006409a36e6291ab7b7102e2ef80d3398ac))
* remove unnecessary power states ([5eeadf1](https://github.com/tinogo/uc-intg-awol-valerion/commit/5eeadf1a7bd95e7b1f773895104e2fe6cbdb6f11))
* rename a method + update docblock ([86a4677](https://github.com/tinogo/uc-intg-awol-valerion/commit/86a46773df3457970e3bd88a89d7370353da77a8))
* satisfy pylint ([fddf816](https://github.com/tinogo/uc-intg-awol-valerion/commit/fddf816969723a343c13b079b6f81d0e29413b90))

## Integration Template Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

_Changes in the next release_
