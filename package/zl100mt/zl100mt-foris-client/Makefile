#
# Copyright (C) 2018 CZ.NIC z.s.p.o. (http://www.nic.cz/)
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=zl100mt-foris-client
PKG_VERSION:=0.5
PKG_RELEASE:=2
PKG_SOURCE_SUBDIR:=$(PKG_NAME)
#PKG_SOURCE_PROTO:=git
#PKG_SOURCE_URL:=https://gitlab.labs.nic.cz/turris/foris-client
#PKG_SOURCE_VERSION:=v$(PKG_VERSION)
#PKG_SOURCE:=$(PKG_NAME)-$(PKG_SOURCE_VERSION).tar.gz
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)
PKG_LICENSE:=GPL-3.0

include $(INCLUDE_DIR)/package.mk
$(call include_mk, python-package.mk)


define Package/$(PKG_NAME)
	TITLE:=zl100mt-foris-client
	CATEGORY:=ZL100MT
	#URL:=https://gitlab.labs.nic.cz/turris/foris-client
	DEPENDS:=+zl100mt-foris-controller
	MAINTAINER:=CZ.NIC <packaging@turris.cz>
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) ./src/* $(PKG_BUILD_DIR)/
endef

define Package/$(PKG_NAME)/description
	An program/library which is act as a client of foris-controller.
endef

define Build/Compile
	$(call Build/Compile/PyMod,,install --prefix=/usr --root=$(PKG_INSTALL_DIR))
endef

define Package/$(PKG_NAME)/conffiles
endef

define Package/$(PKG_NAME)/install
	$(INSTALL_DIR) $(1)
	$(CP) $(PKG_INSTALL_DIR)/* $(1)/
	$(INSTALL_BIN) ./files/foris-client-wrapper $(1)/usr/bin/foris-client-wrapper
	$(INSTALL_BIN) ./files/foris-notify-wrapper $(1)/usr/bin/foris-notify-wrapper
endef


$(eval $(call BuildPackage,$(PKG_NAME)))
