#
# Copyright (C) 2013-2014 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=uboot-zl100mt
PKG_VERSION:=2019.03
PKG_RELEASE:=1
#PKG_SOURCE_PROTO:=git
#PKG_SOURCE_URL:=https://github.com/jia345/zl100mt-uboot.git
#PKG_SOURCE_VERSION:=964b7d631f9d15e252272d5a9073a997c04e3a16
#PKG_SOURCE:=$(PKG_NAME)-$(PKG_SOURCE_VERSION).tar.gz
#PKG_SOURCE_SUBDIR:=turris-omnia-uboot
#PKG_MAINTAINER:=Michal Hrusecky <MichalHrusecky@nic.cz>
#PKG_SOURCE_SUBDIR:=${PKG_NAME}
PKG_SOURCE_SUBDIR:=zl100mt-uboot
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_SOURCE_SUBDIR)

#PKG_LICENSE:=GPL-2.0 GPL-2.0+
#PKG_LICENSE_FILES:=Licenses/README

#include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/kernel.mk
include $(INCLUDE_DIR)/host-build.mk

define Package/${PKG_NAME}
  TITLE:=U-Boot for ZL100MT
  SECTION:=boot
  DESCRIPTION=
  CATEGORY:=Boot Loaders
  DEPENDS:=@TARGET_mvebu_Turris-Omnia uboot-envtools
  URL:=http://www.denx.de/wiki/U-Boot
endef

define Package/${PKG_NAME}/description
  U-Boot bootloader for ZL100MT
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	$(CP) ./src/* $(PKG_BUILD_DIR)/
endef

define Build/Configure
	$(MAKE) -C $(PKG_BUILD_DIR) USE_PRIVATE_LIBGCC=yes db-88f6820-gp_defconfig
endef

define Build/Compile
	$(MAKE) -C $(PKG_BUILD_DIR) CROSS_COMPILE=$(TARGET_CROSS) DTC=$(LINUX_DIR)/scripts/dtc/dtc
	cp $(PKG_BUILD_DIR)/u-boot-spl.kwb $(PKG_BUILD_DIR)/uboot-zl100mt-spl.kwb
	sed -i 's|.*\(CONFIG_MVEBU_BOOTROM_UARTBOOT\).*|\1=y|' $(PKG_BUILD_DIR)/.config
	sed -i 's|spi|uart|' $(PKG_BUILD_DIR)/board/Marvell/db-88f6820-gp/kwbimage.cfg
	$(MAKE) -C $(PKG_BUILD_DIR) CROSS_COMPILE=$(TARGET_CROSS) DTC=$(LINUX_DIR)/scripts/dtc/dtc
	cp $(PKG_BUILD_DIR)/u-boot-spl.kwb $(PKG_BUILD_DIR)/uboot-zl100mt-uart-spl.kwb
	mkdir -p $(HOST_BUILD_DIR)/$(PKG_SOURCE_SUBDIR)
	$(HOSTCC) $(HOST_CFLAGS) -static -o $(HOST_BUILD_DIR)/$(PKG_SOURCE_SUBDIR)/kwboot $(PKG_BUILD_DIR)/tools/kwboot.c
	$(HOSTCC) $(HOST_CFLAGS) -static -o $(HOST_BUILD_DIR)/$(PKG_SOURCE_SUBDIR)/sendbeacon ./files/sendbeacon.c
endef

define Package/${PKG_NAME}/install
	$(INSTALL_DIR) $(1)/boot/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/uboot-zl100mt-spl.kwb $(1)/boot/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/uboot-zl100mt-uart-spl.kwb $(1)/boot/
	$(INSTALL_BIN) $(HOST_BUILD_DIR)/$(PKG_SOURCE_SUBDIR)/kwboot $(HOST_INSTALL_DIR)
	$(INSTALL_BIN) $(HOST_BUILD_DIR)/$(PKG_SOURCE_SUBDIR)/sendbeacon $(HOST_INSTALL_DIR)
endef

$(eval $(call BuildPackage,$(PKG_NAME)))
