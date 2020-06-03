/*
 * (C) Copyright 2013 Codethink Limited
 * Btrfs port to Uboot by
 * Adnan Ali <adnan.ali@codethink.co.uk>
 * See file CREDITS for list of people who contributed to this
 * project.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston,
 * MA 02111-1307 USA
 */

/*
 * Boot support
 */
#include <fs.h>
#include <btrfs.h>

char subvolname[BTRFS_MAX_SUBVOL_NAME];

int do_btr_fsload(cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[])
{
	if (argc > 5) {
		strcpy(subvolname, argv[5]);
		argc--;
	}
	else
		subvolname[0] = '\0';

	return do_load(cmdtp, flag, argc, argv, FS_TYPE_BTR);
}


U_BOOT_CMD(
btrload,        7,      0,      do_btr_fsload,
	"load binary file from a btr filesystem",
	"<interface> [<dev[:part]>]  <addr> <filename> [subvol_name]\n"
	"    - Load binary file 'filename' from 'dev' on 'interface'\n"
	"      to address 'addr' from better filesystem.\n"
	"      the load stops on end of file.\n"
	"      subvol_name is used read that file from this subvolume.\n"
	"      All numeric parameters are assumed to be hex."
);

static int do_btr_ls(cmd_tbl_t *cmdtp, int flag, int argc, char * const argv[])
{
	if (argc > 4) {
                strcpy(subvolname, argv[4]);
		argc--;
	}
        else
                subvolname[0] = '\0';

	return do_ls(cmdtp, flag, argc, argv, FS_TYPE_BTR);
}

U_BOOT_CMD(
	btrls,  5,      1,      do_btr_ls,
	"list files in a directory (default /)",
	"<interface> [<dev[:part]>] [directory] [subvol_name]\n"
	"    - list files from 'dev' on 'interface' in a 'directory'\n"
	"	subvol_name is used read that file from this subvolume."
);

