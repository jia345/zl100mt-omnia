0.9.4 (2018-05-22)
------------------

* lan: guest network and sqm service fix
* wan: 6in4 support
* wan: 6to4 support
* wan: handle missing wan6 section
* uci: character `'` in values
* time: default value for ntp.enabled

0.9.3 (2018-04-26)
------------------

* wifi module: possible device path fix

0.9.2 (2018-04-17)
------------------

* updater module: new call get_enabled
* data_collect module: redownload registration code when router is not found
* wan module: new configuration options (duid, dhcp hostname) + some fixes
* wifi module: reset action added
* uci backend: import command added

0.9.1 (2018-03-23)
------------------

* syslog support removed (should be handled elsewhere)
* data_collect: remove i_agree_datacollect
* wifi: api updates

0.9 (2018-03-21)
----------------

* wifi module
* uci api update (reading anonymous section)
* foris-notify (some fixes)
* updater module & updater integration into other modules (maintain, web, data_collect)
* wan module - small fixes
* client socket (see doc/client_socket)

0.8.4 (2018-02-23)
------------------

* wan module added
* CI install updates
* connection test moved from dns to wan module
* router_notifications module added
* some schema fixes
* notifications count added to web module (get_data)

0.8.3 (2018-02-07)
------------------

* data_collect fixes
* services backend fail_on_error fix
* time module added

0.8.2 (2018-01-15)
------------------

* CI test are using openwrt backend as well as mock backend
* tests for sample plugin integrated into our CI
* tests can use a varios kind of overrides of fixtures (mostly to alter files paths)
* bigger tests refactoring (part of the tests moved to foris-controller-testtools repo)
* lan module implemented
* new functionality added to data_collect module

0.8.1 (2017-12-20)
------------------

* new password module added
* cmdline backend multiline fixes
* about module version parsing fixes

0.8 (2017-12-13)
----------------

* web module api updates
* maintain module added
* support for long messages (>1MB)
* --extra-module-path (set extra modules from cmdline)
* cmdline changes `-m mod1,mod2` -> `-m mod1 -m mod2`

0.7.3 (2017-12-07)
------------------

* about module - fix for older turris

0.7.2 (2017-11-29)
------------------

* dns module - use default value when an option is not present in uci
* uci - default argument to get_{named,anonymous}_option

0.7.1 (2017-11-16)
------------------

* async commands - python buffer fixes
* async commands - match stderr as well
* uci - added replace_list function

0.7 (2017-11-07)
----------------

* added backend to handle async commands
* dns module - connection check handling

0.6.2 (2017-10-31)
------------------

* uci backend fix
* web module - language switch fix

0.6.1 (2017-10-24)
------------------

* dns module reload fix
* calling external programs should be faster

0.6 (2017-10-20)
----------------

* support for sending notifications added (+docs +tests)
* added an option to put logging output into a file
* some fixes
* some code cleanup
* some documentation added

0.5 (2017-10-02)
----------------

* dns module (several option regarding dns)
* web module (language switch)
* wrapper around system services (start, stop, reload, ...)
* wrapper around uci command

0.4 (2017-09-06)
----------------

* docs updates
* put stack traces to error msgs
* write stack traces to debug console
* syslog integration

0.3 (2017-09-04)
----------------

* registration number call added
* contract valid call added
* router registered call added

0.2 (2017-08-23)
----------------

* --single argument for ubus
* making modules and backends modular
* locking moved to backends


0.1 (2017-08-07)
----------------

* initial version
