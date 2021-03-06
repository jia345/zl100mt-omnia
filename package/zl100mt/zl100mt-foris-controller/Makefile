#
# Copyright (C) 2018 CZ.NIC z.s.p.o. (http://www.nic.cz/)
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=zl100mt-foris-controller
PKG_VERSION:=0.9.4
PKG_RELEASE:=1
PKG_SOURCE_SUBDIR:=$(PKG_NAME)
#PKG_SOURCE_PROTO:=git
#PKG_SOURCE_URL:=https://gitlab.labs.nic.cz/turris/foris-controller
#PKG_SOURCE_VERSION:=v$(PKG_VERSION)
#PKG_SOURCE:=$(PKG_NAME)-$(PKG_SOURCE_VERSION).tar.gz
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)
PKG_LICENSE:=GPL-3.0

include $(INCLUDE_DIR)/package.mk
$(call include_mk, python-package.mk)


define Package/$(PKG_NAME)
	TITLE:=zl100mt-foris-controller
	CATEGORY:=ZL100MT
	#URL:=https://gitlab.labs.nic.cz/turris/foris-controller
	DEPENDS:=\
		+python-light +python-ubus +python-prctl +python-multiprocessing +python-pbkdf2 \
		+zl100mt-foris-schema +server-uplink +turris-maintain +user_notify \
		+l10n_supported +sqm-scripts
	MAINTAINER:=CZ.NIC <packaging@turris.cz>
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) ./src/* $(PKG_BUILD_DIR)/
endef

define Package/$(PKG_NAME)/description
	An program which is placed in top of a message bus and translates requests to commands for backends.
endef

define Build/Compile
	$(call Build/Compile/PyMod,,install --prefix=/usr --root=$(PKG_INSTALL_DIR))
endef

define Package/$(PKG_NAME)/conffiles
/etc/config/foris-controller
endef

define Package/$(PKG_NAME)/install
	$(INSTALL_DIR) $(1)
	$(CP) $(PKG_INSTALL_DIR)/* $(1)/
	$(INSTALL_DIR) $(1)/etc/config/
	$(INSTALL_CONF) ./files/foris-controller.conf $(1)/etc/config/foris-controller
	$(INSTALL_DIR) $(1)/etc/init.d/
	$(INSTALL_BIN) ./files/foris-controller.init $(1)/etc/init.d/foris-controller
endef

define Package/$(PKG_NAME)/postinst
#!/bin/sh
set -x
[ -n "$$IPKG_INSTROOT" ] || {
/etc/init.d/foris-controller enable
/etc/init.d/foris-controller restart
}
endef

define Package/$(PKG_NAME)/prerm
#!/bin/sh
set -x
/etc/init.d/foris-controller stop
/etc/init.d/foris-controller disable
endef

$(eval $(call BuildPackage,$(PKG_NAME)))
