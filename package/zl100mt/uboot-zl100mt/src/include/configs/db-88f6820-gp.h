/*
 * Copyright (C) 2014 Stefan Roese <sr@denx.de>
 *
 * SPDX-License-Identifier:	GPL-2.0+
 */

#ifndef _CONFIG_DB_88F6820_GP_H
#define _CONFIG_DB_88F6820_GP_H

/*#define CONFIG_CUSTOMER_BOARD_SUPPORT */
#define CONFIG_TURRISOMNIA_SUPPORT

/*
 * High Level Configuration Options (easy to change)
 */
#define CONFIG_ARMADA_XP		/* SOC Family Name */
#define CONFIG_ARMADA_38X
#define CONFIG_DB_88F6820_GP		/* Board target name for DDR training */

#define CONFIG_SYS_L2_PL310

#ifdef CONFIG_SPL_BUILD
#define CONFIG_SKIP_LOWLEVEL_INIT	/* disable board lowlevel_init */
#endif
#define CONFIG_SYS_GENERIC_BOARD
#define CONFIG_DISPLAY_BOARDINFO_LATE

#define CONFIG_BOARD_LATE_INIT

/*
 * TEXT_BASE needs to be below 16MiB, since this area is scrubbed
 * for DDR ECC byte filling in the SPL before loading the main
 * U-Boot into it.
 */
#define	CONFIG_SYS_TEXT_BASE	0x00800000
#define CONFIG_SYS_TCLK		250000000	/* 250MHz */

/*
 * Commands configuration
 */
#define CONFIG_CMD_BOOTZ
#define CONFIG_SYS_NO_FLASH		/* Declare no flash (NOR/SPI) */
#define CONFIG_CMD_CACHE
#define CONFIG_CMD_ENV
#define CONFIG_CMD_EXT2
#define CONFIG_CMD_EXT4
#define CONFIG_CMD_FAT
#define CONFIG_CMD_BTR
#define CONFIG_CMD_FS_GENERIC
#define CONFIG_CMD_MMC
#define CONFIG_CMD_PCI
#define CONFIG_CMD_SCSI
#define CONFIG_CMD_SPI
#define CONFIG_CMD_SF
#define CONFIG_CMD_TFTPPUT
#define CONFIG_CMD_TIME

/* RAW initrd support */
#define CONFIG_SUPPORT_RAW_INITRD

/* I2C */
#define CONFIG_SYS_I2C
#define CONFIG_SYS_I2C_MVTWSI
#define CONFIG_I2C_MVTWSI_BASE0		MVEBU_TWSI_BASE
#define CONFIG_SYS_I2C_SLAVE		0x0
#define CONFIG_SYS_I2C_SPEED		100000

#define CONFIG_SYS_I2C_DIRECT_BUS

#undef CONFIG_SYS_NUM_I2C_BUSES
#define CONFIG_SYS_NUM_I2C_BUSES	1
/*
#define CONFIG_SYS_NUM_I2C_BUSES	8
#define CONFIG_SYS_I2C_MAX_HOPS		1
#define CONFIG_SYS_I2C_BUSES	{	{0, {I2C_NULL_HOP} }, \
					{0, {{I2C_MUX_PCA9547, 0x70, 0} } }, \
					{0, {{I2C_MUX_PCA9547, 0x70, 1} } }, \
					{0, {{I2C_MUX_PCA9547, 0x70, 2} } }, \
					{0, {{I2C_MUX_PCA9547, 0x70, 3} } }, \
					{0, {{I2C_MUX_PCA9547, 0x70, 4} } }, \
					{0, {{I2C_MUX_PCA9547, 0x70, 5} } }, \
					{0, {{I2C_MUX_PCA9547, 0x70, 6} } }, \
				}
*/

#define CONFIG_ATSHA204
#define CONFIG_ATSHA204_ADDR	0x64

/* Watchdog */
#ifndef CONFIG_SPL_BUILD
#define CONFIG_HW_WATCHDOG
#define CONFIG_ORION_WATCHDOG
#endif

/* SPI NOR flash default params, used by sf commands */
#define CONFIG_SF_DEFAULT_SPEED		1000000
#define CONFIG_SF_DEFAULT_MODE		SPI_MODE_3
/*#define CONFIG_SPI_FLASH_STMICRO*/
#define CONFIG_SPI_FLASH_SPANSION
#define CONFIG_SPI_FLASH_BAR

/*
 * SDIO/MMC Card Configuration
 */
#define CONFIG_MMC
#define CONFIG_MMC_SDMA
#define CONFIG_GENERIC_MMC
#define CONFIG_SDHCI
#define CONFIG_MV_SDHCI
#define CONFIG_SYS_MMC_BASE		MVEBU_SDIO_BASE

/*
 * SATA/SCSI/AHCI configuration
 */
#define CONFIG_LIBATA
#define CONFIG_SCSI_AHCI
#define CONFIG_SCSI_AHCI_PLAT
#define CONFIG_SYS_SCSI_MAX_SCSI_ID	2
#define CONFIG_SYS_SCSI_MAX_LUN		1
#define CONFIG_SYS_SCSI_MAX_DEVICE	(CONFIG_SYS_SCSI_MAX_SCSI_ID * \
					 CONFIG_SYS_SCSI_MAX_LUN)

/* Partition support */
#define CONFIG_DOS_PARTITION
#define CONFIG_EFI_PARTITION

/* Additional FS support/configuration */
#define CONFIG_SUPPORT_VFAT

/* USB/EHCI configuration */
#define CONFIG_EHCI_IS_TDI

/* Environment in SPI NOR flash */
#define CONFIG_ENV_IS_IN_SPI_FLASH
#define CONFIG_ENV_OFFSET		(3*(1 << 18)) /* 786KiB in */
#define CONFIG_ENV_SIZE			(64 << 10) /* 64KiB */
#define CONFIG_ENV_SECT_SIZE		(256 << 10) /* 256KiB sectors */

#define CONFIG_PHY_MARVELL		/* there is a marvell phy */
#define CONFIG_PHY_ADDR			{ 5, 6, 1 }
/*#define CONFIG_SYS_NETA_INTERFACE_TYPE	PHY_INTERFACE_MODE_RGMII*/
#define CONFIG_SYS_NETA_INTERFACE_TYPE	{ PHY_INTERFACE_MODE_RGMII, PHY_INTERFACE_MODE_RGMII, PHY_INTERFACE_MODE_SGMII }
#define PHY_ANEG_TIMEOUT	8000	/* PHY needs a longer aneg time */

/* PCIe support */
#define CONFIG_PCI
#define CONFIG_PCI_MVEBU
#define CONFIG_PCI_PNP
#define CONFIG_PCI_SCAN_SHOW
#define CONFIG_E1000	/* enable Intel E1000 support for testing */

#define CONFIG_SYS_CONSOLE_INFO_QUIET	/* don't print console @ startup */
#define CONFIG_SYS_ALT_MEMTEST

/* Default boot environment. */
/* #define CONFIG_BOOTCOMMAND "i2c dev 1; i2c read 0x2a 0x9 1 0x00FFFFF0; setexpr.b rescue *0x00FFFFF0; if test $rescue -ge 1; then echo BOOT RESCUE; run rescueboot; else echo BOOT eMMC FS; run mmcboot; fi" */
#define CONFIG_BOOTCOMMAND "echo BOOT eMMC FS; run mmcboot"

/* Keep device tree and initrd in lower memory so the kernel can access them */
#define	CONFIG_EXTRA_ENV_SETTINGS \
	"fdt_high=0x10000000\0" \
	"initrd_high=0x10000000\0" \
	"ethact=neta2\0" \
	"mmcboot=setenv bootargs \"$bootargs cfg80211.freg=$regdomain\"; btrload mmc 0 0x01000000 boot/zImage @; btrload mmc 0 0x02000000 boot/dtb @; bootz 0x01000000 - 0x02000000\0" \
	"rescueboot=i2c mw 0x2a.1 0x3 0x1c 1; i2c mw 0x2a.1 0x4 0x1c 1; mw.l 0x01000000 0x00ff000c; i2c write 0x01000000 0x2a.1 0x5 4 -s; setenv bootargs \"$bootargs omniarescue=$rescue\"; sf probe; sf read 0x1000000 0x100000 0x700000; bootz 0x1000000\0" \
	"bootargs=earlyprintk console=ttyS0,115200 rootfstype=btrfs rootdelay=2 root=b301 rootflags=subvol=@,commit=5 rw\0"


/* SPL */
/*
 * Select the boot device here
 *
 * Currently supported are:
 * SPL_BOOT_SPI_NOR_FLASH	- Booting via SPI NOR flash
 * SPL_BOOT_SDIO_MMC_CARD	- Booting via SDIO/MMC card (partition 1)
 */
#define SPL_BOOT_SPI_NOR_FLASH		1
#define SPL_BOOT_SDIO_MMC_CARD		2
#define CONFIG_SPL_BOOT_DEVICE		SPL_BOOT_SPI_NOR_FLASH

/* Defines for SPL */
#define CONFIG_SPL_FRAMEWORK
#define CONFIG_SPL_SIZE			(140 << 10)
#define CONFIG_SPL_TEXT_BASE		0x40000030
#define CONFIG_SPL_MAX_SIZE		(CONFIG_SPL_SIZE - 0x0030)

#define CONFIG_SPL_BSS_START_ADDR	(0x40000000 + CONFIG_SPL_SIZE)
#define CONFIG_SPL_BSS_MAX_SIZE		(16 << 10)

#define CONFIG_SYS_SPL_MALLOC_START	(CONFIG_SPL_BSS_START_ADDR + \
					 CONFIG_SPL_BSS_MAX_SIZE)
#define CONFIG_SYS_SPL_MALLOC_SIZE	(16 << 10)

#define CONFIG_SPL_STACK		(0x40000000 + ((192 - 16) << 10))
#define CONFIG_SPL_BOOTROM_SAVE		(CONFIG_SPL_STACK + 4)

#define CONFIG_SPL_LIBCOMMON_SUPPORT
#define CONFIG_SPL_LIBGENERIC_SUPPORT
#define CONFIG_SPL_SERIAL_SUPPORT
#define CONFIG_SPL_I2C_SUPPORT
#define CONFIG_SPL_MISC_SUPPORT

#if CONFIG_SPL_BOOT_DEVICE == SPL_BOOT_SPI_NOR_FLASH
/* SPL related SPI defines */
#define CONFIG_SPL_SPI_SUPPORT
#define CONFIG_SPL_SPI_FLASH_SUPPORT
#define CONFIG_SPL_SPI_LOAD
#define CONFIG_SPL_SPI_BUS		0
#define CONFIG_SPL_SPI_CS		0
#define CONFIG_SYS_SPI_U_BOOT_OFFS	0x20000
#define CONFIG_SYS_U_BOOT_OFFS		CONFIG_SYS_SPI_U_BOOT_OFFS
#endif

#if CONFIG_SPL_BOOT_DEVICE == SPL_BOOT_SDIO_MMC_CARD
/* SPL related MMC defines */
#define CONFIG_SPL_MMC_SUPPORT
#define CONFIG_SPL_LIBDISK_SUPPORT
#define CONFIG_SYS_MMCSD_RAW_MODE_U_BOOT_PARTITION 1
#define CONFIG_SYS_MMC_U_BOOT_OFFS		(160 << 10)
#define CONFIG_SYS_U_BOOT_OFFS			CONFIG_SYS_MMC_U_BOOT_OFFS
#define CONFIG_SYS_MMCSD_RAW_MODE_U_BOOT_SECTOR	(CONFIG_SYS_U_BOOT_OFFS / 512)
#define CONFIG_SYS_U_BOOT_MAX_SIZE_SECTORS	((512 << 10) / 512) /* 512KiB */
#ifdef CONFIG_SPL_BUILD
#define CONFIG_FIXED_SDHCI_ALIGNED_BUFFER	0x00180000	/* in SDRAM */
#endif
#endif

/* Enable DDR support in SPL (DDR3 training from Marvell bin_hdr) */
#define CONFIG_SYS_MVEBU_DDR_A38X
#define CONFIG_DDR3

/*
 * mv-common.h should be defined after CMD configs since it used them
 * to enable certain macros
 */
#include "mv-common.h"

#endif /* _CONFIG_DB_88F6820_GP_H */
