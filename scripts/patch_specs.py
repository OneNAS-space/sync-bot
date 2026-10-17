#!/usr/bin/env python3
"""
所有自动生成补丁的定义。
 
每条 spec 的字段：
  tree              : 目标源码树，见 apply_dynamic_patches.py 里的 TREES（不写默认 'kernel'）
  name              : 输出补丁文件名（不含 .patch），同名的多条 spec 会合并进同一份补丁
  filename          : 目标文件名
  path_must_contain : 元组，full_path 必须包含的每一段子串（粗筛，可能有误伤，配合 parent_dir_exact 精确排除）
  parent_dir_exact  : 可选，要求文件的直接父目录名完全等于这个值（用于排除 wifi7 这类同名变体子目录）
  kind              : 'literal' 用 str.replace，'regex' 用 re.subn
  replacements      : [(old_or_pattern, new_or_repl), ...]，按顺序依次作用在同一份 content 上
"""

PATCH_HEADERS = { 
    '0363-net-ethernet-qualcomm-honor-safe-NAPI-budgets': {
        'author': 'Yang Zhengguo <yangzhgg@gmail.com>',
        'date': 'Sun, 16 Aug 2026 00:41:53 +0800',
        'subject': 'net: ethernet: qualcomm: honor safe NAPI budgets',
        'body': (
            "The EDMA module parameters are validated and reported, but the NAPI instances\n"
            "are registered with the fixed values from edma_hw_info instead.  On IPQ9574\n"
            "the TX value is 512, which makes the networking core emit a warning because\n"
            "it exceeds NAPI_POLL_WEIGHT.\n"
            "\n"
            "Use the validated module parameters when registering RX and TX NAPI, limit\n"
            "them to the networking core's standard budget, and make the IPQ9574 fallback\n"
            "safe as well."
        ),
        'signed_off_by': [
            'Yang Zhengguo <yangzhgg@gmail.com>',
            'Jackie Han <jackie.han@gmail.com>',
        ],
    },

    '0364-regulator-qcom_smd-fix-MP5496-supply-names': {
        'author': 'Gabor Juhos <j4g8y7@gmail.com>',
        'date': 'Tue, 16 Dec 2025 19:38:00 +0100',
        'subject': 'regulator: qcom_smd: change MP5496 supply names',
        'body': (
            'The MP5496 regulator data uses the regulator output name as its input\n'
            'supply name.  This can make the regulator core resolve an output to\n'
            'itself and reject it, for example:\n'
            '\n'
            '  Supply for s1 (s1) resolved to itself\n'
            '\n'
            'Use the MP5496 input pin names from the datasheet.  Buck 1 is supplied\n'
            'by VIN1, while Buck 2 and LDO2 share VIN2.  LDO5 is supplied by VIN5.\n'
            '\n'
            'Link: https://lore.kernel.org/r/20251216-qcom_smd-mp5496-supply-fix-v1-1-f9b5e70536de@gmail.com'
        ),
        'signed_off_by': ['Gabor Juhos <j4g8y7@gmail.com>'],
    },

    '0365-net-ethernet-qualcomm-ppe-defer-phylink-setup': {
        'author': 'Jackie Han <jackie.han@gmail.com>',
        'date': 'Sun, 11 Oct 2026 07:50:00 +0800',
        'subject': 'net: ethernet: qualcomm: ppe: defer phylink setup to after netdev registration',
        'body': (
            'edma_port_setup() attaches the PHY, through ppe_port_phylink_setup(),\n'
            'before the netdev is registered.  The PHY attach message is therefore\n'
            'printed for a netdev that is still unregistered:\n'
            '\n'
            '  qcom_ppe 3a000000.ethernet lan2 (uninitialized): PHY [...] driver [...]\n'
            '\n'
            'Register the netdev first and set up phylink afterwards.  If\n'
            'ppe_port_phylink_setup() fails, it has already released its own phylink\n'
            'and PCS, so only the netdev has to be unregistered before the common\n'
            'cleanup.'
        ),
        'signed_off_by': ['Jackie Han <jackie.han@gmail.com>'],
    },
 
    '0366-net-ethernet-qualcomm-ppe-clear-error-pointers-on-phylink-setup-failure': {
        'author': 'Jackie Han <jackie.han@gmail.com>',
        'date': 'Sun, 11 Oct 2026 08:10:00 +0800',
        'subject': 'net: ethernet: qualcomm: ppe: clear error pointers on phylink setup failure',
        'body': (
            'ppe_port_phylink_setup() assigns the result of ipq_pcs_get() and\n'
            'phylink_create() directly to ppe_port->pcs and ppe_port->phylink.  If\n'
            'either call fails, the ERR_PTR value is left in the structure.\n'
            '\n'
            'ppe_port_phylink_destroy() only checks these members for NULL, so any\n'
            'later call on the same port would hand the error pointer to\n'
            'ipq_pcs_put(), phylink_disconnect_phy() and phylink_destroy().\n'
            '\n'
            'Set both members to NULL when the calls fail.  The success path is\n'
            'unchanged.'
        ),
        'signed_off_by': ['Jackie Han <jackie.han@gmail.com>'],
    },

    '0367-net-ethernet-qualcomm-ppe-guard-ethtool-against-missing-phylink': {
        'author': 'Jackie Han <jackie.han@gmail.com>',
        'date': 'Mon, 12 Oct 2026 10:30:00 +0800',
        'subject': 'net: ethernet: qualcomm: ppe: guard ethtool callbacks against missing phylink',
        'body': (
            'Since phylink is now set up after register_netdev() in\n'
            'edma_port_setup(), ppe_port->phylink is still NULL for a short time\n'
            'after the netdev becomes visible.  The ethtool callbacks for link\n'
            'settings and pause parameters pass it to phylink without checking, and\n'
            'would dereference a NULL pointer if called in that window.\n'
            '\n'
            'Return -EOPNOTSUPP from the callbacks that return a value, and skip the\n'
            'call in edma_get_pauseparam(), when phylink is not available.  This\n'
            'matches edma_port_open(), edma_port_close() and edma_port_ioctl(),\n'
            'which already check ppe_port->phylink.'
        ),
        'signed_off_by': ['Jackie Han <jackie.han@gmail.com>'],
    },

    '980-AP-keep_configured_width_on_5G_6G-if_20M_40M_scan_fails': {
        'author': 'Crescentm <guyues@outlook.com>',
        'date': 'Thu, 1 Oct 2026 15:13:53 +0800',
        'subject': 'AP: keep the configured width on 5/6 GHz if the 20/40 MHz scan fails',
        'body': (
            "Before enabling a 40 MHz (or wider) BSS, hostapd scans the affected\n"
            "channels for overlapping BSSes. If the driver refuses the scan with\n"
            "-EBUSY, ap_ht40_scan_retry() tries again once a second, and after 15\n"
            "attempts brings the BSS up at 20 MHz.\n"
            "\n"
            "On a single wiphy with several radios (e.g. ath12k with a 2.4, 5 and\n"
            "6 GHz radio) only one radio can scan at a time, so while another radio\n"
            "scans (ACS, its own coexistence scan, a station scan), the 5 GHz or 6 GHz\n"
            "radio can run out of retries and comes up at 20 MHz, although nothing\n"
            "on the channel asked for that.\n"
            "\n"
            "On 5/6 GHz the result of that scan can only swap the primary and\n"
            "secondary channel: check_40mhz_5g() returns 1 or 2 for any valid channel\n"
            "pair and never disallows 40 MHz. Skipping it is what noscan=1 already\n"
            "does. So when the scan cannot be run there, keep the configured channel\n"
            "width and bring the BSS up as configured. 2.4 GHz still falls back to\n"
            "20 MHz, since there the scan can forbid 40 MHz."
        ),
        'signed_off_by': ['Crescentm <guyues@outlook.com>'],
    },
}
    
PATCH_SPECS = [
    {
        'name': '0363-net-ethernet-qualcomm-honor-safe-NAPI-budgets',
        'filename': 'edma.c',
        'path_must_contain': ('ethernet', 'qualcomm', 'ppe'),
        'kind': 'regex',
        'replacements': [
            (r'MODULE_PARM_DESC\(\s*edma_rx_napi_budget\s*,\s*".*?"\s*\)',
             'MODULE_PARM_DESC(edma_rx_napi_budget, "Rx NAPI budget (default:32, min:16, max:64)")'),
            (r'MODULE_PARM_DESC\(\s*edma_tx_napi_budget\s*,\s*".*?"\s*\)',
             'MODULE_PARM_DESC(edma_tx_napi_budget, "Tx NAPI budget (default:64, min:16, max:64)")'),
            (r'\.napi_budget_tx\s*=\s*\d+\s*,', '.napi_budget_tx = 64,'),
        ],
    },
    {
        'name': '0363-net-ethernet-qualcomm-honor-safe-NAPI-budgets',
        'filename': 'edma_cfg_rx.c',
        'path_must_contain': ('ethernet', 'qualcomm', 'ppe'),
        'kind': 'regex',
        'replacements': [(r'(edma_rx_napi_poll,\s*)hw_info->napi_budget_rx', r'\1edma_rx_napi_budget')],
    },
    {
        'name': '0363-net-ethernet-qualcomm-honor-safe-NAPI-budgets',
        'filename': 'edma_cfg_rx.h',
        'path_must_contain': ('ethernet', 'qualcomm', 'ppe'),
        'kind': 'regex',
        'replacements': [
            (r'#define\s+EDMA_RX_NAPI_WORK_DEF\s+\d+', '#define EDMA_RX_NAPI_WORK_DEF\t\t32'),
            (r'#define\s+EDMA_RX_NAPI_WORK_MAX\s+\d+', '#define EDMA_RX_NAPI_WORK_MAX\t\t64'),
        ],
    },
    {
        'name': '0363-net-ethernet-qualcomm-honor-safe-NAPI-budgets',
        'filename': 'edma_cfg_tx.c',
        'path_must_contain': ('ethernet', 'qualcomm', 'ppe'),
        'kind': 'regex',
        'replacements': [(r'(edma_tx_napi_poll,\s*)hw_info->napi_budget_tx', r'\1edma_tx_napi_budget')],
    },
    {
        'name': '0363-net-ethernet-qualcomm-honor-safe-NAPI-budgets',
        'filename': 'edma_cfg_tx.h',
        'path_must_contain': ('ethernet', 'qualcomm', 'ppe'),
        'kind': 'regex',
        'replacements': [
            (r'#define\s+EDMA_TX_NAPI_WORK_DEF\s+\d+', '#define EDMA_TX_NAPI_WORK_DEF\t64'),
            (r'#define\s+EDMA_TX_NAPI_WORK_MAX\s+\d+', '#define EDMA_TX_NAPI_WORK_MAX\t64'),
        ],
    },
    {
        'name': '0364-regulator-qcom_smd-fix-MP5496-supply-names',
        'filename': 'qcom_smd-regulator.c',
        'path_must_contain': ('regulator',),
        'kind': 'literal',
        'replacements': [
            ('{ "s1", QCOM_SMD_RPM_SMPA, 1, &mp5496_smps, "s1" },',
             '{ "s1", QCOM_SMD_RPM_SMPA, 1, &mp5496_smps, "vin1" },'),
            ('{ "s2", QCOM_SMD_RPM_SMPA, 2, &mp5496_smps, "s2" },',
             '{ "s2", QCOM_SMD_RPM_SMPA, 2, &mp5496_smps, "vin2" },'),
            ('{ "l2", QCOM_SMD_RPM_LDOA, 2, &mp5496_ldoa2, "l2" },',
             '{ "l2", QCOM_SMD_RPM_LDOA, 2, &mp5496_ldoa2, "vin2" },'),
            ('{ "l5", QCOM_SMD_RPM_LDOA, 5, &mp5496_ldoa2, "l5" },',
             '{ "l5", QCOM_SMD_RPM_LDOA, 5, &mp5496_ldoa2, "vin5" },'),
        ],
    },
    {
        'name': '0365-net-ethernet-qualcomm-ppe-defer-phylink-setup',
        'filename': 'edma_port.c',
        'path_must_contain': ('ethernet', 'qualcomm', 'ppe'),
        'kind': 'regex',
        'replacements': [
            (
                # edma_port_setup(): configure -> phylink setup -> register_netdev -> done -> error labels
                r'(?s)(?P<indent>[ \t]*)edma_port_configure\(netdev\);\s*\n\s*'
                r'ret\s*=\s*ppe_port_phylink_setup\(port,\s*netdev\);\s*\n'
                r'(?P<phylink_if>[ \t]*if\s*\(ret\)\s*\{.+?\})\s*\n\s*'
                r'ret\s*=\s*register_netdev\(netdev\);\s*\n'
                r'(?P<netdev_if>[ \t]*if\s*\(ret\)\s*\{.+?\})\s*\n\s*'
                r'netdev_dbg\(netdev,\s*"Setup EDMA port%d done\\n",\s*port_id\);\s*\n\s*'
                r'return\s+ret;\s*\n\s*'
                r'register_netdev_fail:\s*\n\s*'
                r'ppe_port_phylink_destroy\(port\);\s*\n\s*'
                r'port_phylink_setup_fail:',

                # register_netdev() first, then phylink setup. ppe_port_phylink_setup()
                # cleans up after itself on failure, so the error path must not destroy it again.
                r'\g<indent>edma_port_configure(netdev);\n\n'
                r'\g<indent>ret = register_netdev(netdev);\n'
                r'\g<netdev_if>\n\n'
                r'\g<indent>ret = ppe_port_phylink_setup(port, netdev);\n'
                r'\g<phylink_if>\n\n'
                r'\g<indent>netdev_dbg(netdev, "Setup EDMA port%d done\\n", port_id);\n'
                r'\g<indent>return ret;\n\n'
                r'port_phylink_setup_fail:\n'
                r'\g<indent>unregister_netdev(netdev);\n'
                r'register_netdev_fail:',
                1,
            ),
        ],
    },
    {
        'name': '0366-net-ethernet-qualcomm-ppe-clear-error-pointers-on-phylink-setup-failure',
        'filename': 'ppe_port.c',
        'path_must_contain': ('ethernet', 'qualcomm', 'ppe'),
        'kind': 'regex',
        'replacements': [
            (
                r'(?P<i>[ \t]*)return\s+PTR_ERR\(ppe_port->pcs\);',
                r'\g<i>ret = PTR_ERR(ppe_port->pcs);\n'
                r'\g<i>ppe_port->pcs = NULL;\n'
                r'\g<i>return ret;',
                1,
            ),
            (
                r'(?P<i>[ \t]*)ret\s*=\s*PTR_ERR\(ppe_port->phylink\);\s*\n\s*goto err_free_pcs;',
                r'\g<i>ret = PTR_ERR(ppe_port->phylink);\n'
                r'\g<i>ppe_port->phylink = NULL;\n'
                r'\g<i>goto err_free_pcs;',
                1,
            ),
        ],
    },
    {
        'name': '0367-net-ethernet-qualcomm-ppe-guard-ethtool-against-missing-phylink',
        'filename': 'edma_ethtool.c',
        'path_must_contain': ('ethernet', 'qualcomm', 'ppe'),
        'kind': 'regex',
        'replacements': [
            # ksettings_get: phylink may not exist yet right after register_netdev()
            (
                r'(?P<i>[ \t]*)return\s+phylink_ethtool_ksettings_get\(port->phylink,\s*cmd\);',
                r'\g<i>if (!port->phylink)\n'
                r'\g<i>\treturn -EOPNOTSUPP;\n\n'
                r'\g<i>return phylink_ethtool_ksettings_get(port->phylink, cmd);',
                1,
            ),
            # ksettings_set
            (
                r'(?P<i>[ \t]*)return\s+phylink_ethtool_ksettings_set\(port->phylink,\s*cmd\);',
                r'\g<i>if (!port->phylink)\n'
                r'\g<i>\treturn -EOPNOTSUPP;\n\n'
                r'\g<i>return phylink_ethtool_ksettings_set(port->phylink, cmd);',
                1,
            ),
            # get_pauseparam is void: skip the call, the core has already zeroed @pause
            (
                r'(?P<i>[ \t]*)phylink_ethtool_get_pauseparam\(port->phylink,\s*pause\);',
                r'\g<i>if (port->phylink)\n'
                r'\g<i>\tphylink_ethtool_get_pauseparam(port->phylink, pause);',
                1,
            ),
            # set_pauseparam
            (
                r'(?P<i>[ \t]*)return\s+phylink_ethtool_set_pauseparam\(port->phylink,\s*pause\);',
                r'\g<i>if (!port->phylink)\n'
                r'\g<i>\treturn -EOPNOTSUPP;\n\n'
                r'\g<i>return phylink_ethtool_set_pauseparam(port->phylink, pause);',
                1,
            ),
        ],
    },
    # ---- mac80211 backports tree ----
    #{
    #    'tree': 'mac80211',
    #    'name': '105-wifi-ath12k-support-CV-upload-direct-buffer-module',
    #    'filename': 'wmi.h',
    #    'path_must_contain': ('mac80211', 'backports', 'drivers/net/wireless/ath/ath12k'),
    #    'parent_dir_exact': 'ath12k',
    #    'kind': 'literal',
    #    'replacements': [
    #        (
    #            '\tWMI_DIRECT_BUF_CFR = 1,',
    #            '\tWMI_DIRECT_BUF_CFR = 1,\n\tWMI_DIRECT_BUF_CV_UPLOAD = 2,'
    #        ),
    #    ],
    #},
    {
        'tree': 'mac80211',
        'name': '906-wifi-ath12k-handle-empty-regulatory-events',
        'filename': 'wmi.c',
        'path_must_contain': ('mac80211', 'backports', 'drivers/net/wireless/ath/ath12k'),
        'parent_dir_exact': 'ath12k',
        'kind': 'regex',
        'replacements': [
            # 1. Add status_code local variables (accurately capture the total_reg_rules declaration line)
            (
                r'u32(\s+total_reg_rules\s*=\s*0\s*;)',
                r'u32 status_code __maybe_unused,\1'
            ),
            # 2. Insert status_code parsing switch block (anchored at the beginning of reg_info assigning values to 2G rules)
            (
                r'(\t)(reg_info->num_2g_reg_rules\s*=\s*le32_to_cpu\(ev->num_2g_reg_rules\);)',
                r'\1memcpy(reg_info->alpha2, &ev->alpha2, REG_ALPHA2_LEN);\n'
                r'\1reg_info->dfs_region = le32_to_cpu(ev->dfs_region);\n'
                r'\1reg_info->phybitmap = le32_to_cpu(ev->phybitmap);\n'
                r'\1reg_info->num_phy = le32_to_cpu(ev->num_phy);\n'
                r'\1reg_info->phy_id = le32_to_cpu(ev->phy_id);\n'
                r'\1reg_info->ctry_code = le32_to_cpu(ev->country_id);\n'
                r'\1reg_info->reg_dmn_pair = le32_to_cpu(ev->domain_code);\n\n'
                r'\1status_code = le32_to_cpu(ev->status_code);\n'
                r'\1switch (status_code) {\n'
                r'\1case WMI_REG_SET_CC_STATUS_PASS:\n'
                r'\1\treg_info->status_code = REG_SET_CC_STATUS_PASS;\n'
                r'\1\tbreak;\n'
                r'\1case WMI_REG_CURRENT_ALPHA2_NOT_FOUND:\n'
                r'\1\treg_info->status_code = REG_CURRENT_ALPHA2_NOT_FOUND;\n'
                r'\1\tbreak;\n'
                r'\1case WMI_REG_INIT_ALPHA2_NOT_FOUND:\n'
                r'\1\treg_info->status_code = REG_INIT_ALPHA2_NOT_FOUND;\n'
                r'\1\tbreak;\n'
                r'\1case WMI_REG_SET_CC_CHANGE_NOT_ALLOWED:\n'
                r'\1\treg_info->status_code = REG_SET_CC_CHANGE_NOT_ALLOWED;\n'
                r'\1\tbreak;\n'
                r'\1case WMI_REG_SET_CC_STATUS_NO_MEMORY:\n'
                r'\1\treg_info->status_code = REG_SET_CC_STATUS_NO_MEMORY;\n'
                r'\1\tbreak;\n'
                r'\1case WMI_REG_SET_CC_STATUS_FAIL:\n'
                r'\1\treg_info->status_code = REG_SET_CC_STATUS_FAIL;\n'
                r'\1\tbreak;\n'
                r'\1default:\n'
                r'\1\tath12k_warn(ab, "unknown regulatory status %u\\n", status_code);\n'
                r'\1\treg_info->status_code = REG_SET_CC_STATUS_FAIL;\n'
                r'\1\tbreak;\n'
                r'\1}\n\n'
                r'\1\2'
            ),
            # 3. Empty rule processing: change -EINVAL to -ENODATA and remove the warning
            (
                r'if\s*\(!total_reg_rules\)\s*\{\n[ \t]*ath12k_warn\([^)]+\);\n[ \t]*return\s+-EINVAL;',
                "if (!total_reg_rules) {\n\t\treturn -ENODATA;"
            ),
            # 4. Assign pdev_idx in advance and distinguish -ENODATA branches
            (
                r'(\t)(ret\s*=\s*ath12k_pull_reg_chan_list_ext_update_ev\(ab,\s*skb,\s*reg_info\);\n)'
                r'(?:\s*if\s*\(ret\)\s*\{\n)'
                r'\s*(ath12k_warn\(ab,\s*"failed to extract regulatory info from received event\\n"\);\n)',

                r'\1\2'
                r'\1if ((!ret || ret == -ENODATA) && reg_info->phy_id < ab->num_radios)\n'
                r'\1\tpdev_idx = reg_info->phy_id;\n'
                r'\n'
                r'\1if (ret) {\n'
                r'\1\tif (ret == -ENODATA && pdev_idx != 255) {\n'
                r'\1\t\t/* Keep the last valid regdomain, but finish this update. */\n'
                r'\1\t\tret = ATH12K_REG_STATUS_VALID;\n'
                r'\1\t} else {\n'
                r'\1\t\t\3'
                r'\1\t}\n'
            ),
            # 5. Delete the repeated pdev_idx assignment
            (
                r'(\t/\*\s*free old reg_info if it exist\s*\*/\n)\s*pdev_idx\s*=\s*reg_info->phy_id;\n',
                r'\1'
            ),
        ],
    },
    {
        'tree': 'mac80211',
        'name': '908-wifi-ath12k-use-WSI-index-for-hardware-group-order',
        'filename': 'core.c',
        'path_must_contain': ('mac80211', 'backports', 'drivers/net/wireless/ath/ath12k'),
        'parent_dir_exact': 'ath12k',
        'kind': 'regex',
        'replacements': [
            # 1. Replace the assignment logic of ab->device_id and add the security checksum shelling logic
            (
                r'(\t)ab->device_id\s*=\s*ag->num_probed\+\+;\n'
                r'(\t)ag->ab\[ab->device_id\]\s*=\s*ab;\n'
                r'(\t)ab->ag\s*=\s*ag;',

                r'\1if (wsi->index >= ag->num_devices) {\n'
                r'\1\tath12k_warn(ab, "invalid WSI index %u for group with %d devices\\n",\n'
                r'\1\t\t    wsi->index, ag->num_devices);\n'
                r'\1\tgoto invalid_group;\n'
                r'\1}\n\n'
                r'\1if (ag->ab[wsi->index]) {\n'
                r'\1\tath12k_warn(ab, "duplicate WSI index %u in group %d\\n",\n'
                r'\1\t\t    wsi->index, ag->id);\n'
                r'\1\tgoto invalid_group;\n'
                r'\1}\n\n'
                r'\1ab->device_id = wsi->index;\n'
                r'\2ag->ab[ab->device_id] = ab;\n'
                r'\3ag->num_probed++;\n'
                r'\3ab->ag = ag;'
            ),
            # 2. Replace the ath12k_dbg print information at the bottom (add device_id printing and add \n at the end)
            (
                r'(\t)ath12k_dbg\(ab,\s*ATH12K_DBG_BOOT,\s*"wsi group-id %d num-devices %d index %d",\n'
                r'\t\t\s*ag->id,\s*ag->num_devices,\s*wsi->index\);',

                r'\1ath12k_dbg(ab, ATH12K_DBG_BOOT,\n'
                r'\1\t   "wsi group-id %d num-devices %d index %d device-id %d\\n",\n'
                r'\1\t   ag->id, ag->num_devices, wsi->index, ab->device_id);'
            ),
        ],
    },
    {
        'tree': 'mac80211',
        'name': '909-wifi-ath12k-log-WMI-control-service-topology',
        'filename': 'wmi.c',
        'path_must_contain': ('mac80211', 'backports', 'drivers/net/wireless/ath/ath12k'),
        'parent_dir_exact': 'ath12k',
        'kind': 'regex',
        'replacements': [
            # 1. Add ag and wsi_controller definitions to the local variable declaration
            (
                r'(ath12k_connect_pdev_htc_service[^{]*?\{\n[ \t]*int status;)',
                r'\1\n\tstruct ath12k_hw_group *ag = ath12k_ab_to_ag(ab);\n\tbool wsi_controller;'
            ),
            # 2. Parse the wsi-controller node and output the topology Debug log before connecting
            (
                r'(\tconn_req\.service_id\s*=\s*svc_id\[pdev_idx\];\n)',
                r'\1\n'
                r'\twsi_controller = ab->dev->of_node &&\n'
                r'\t\tof_property_read_bool(ab->dev->of_node, "qcom,wsi-controller");\n\n'
                r'\tath12k_dbg(ab, ATH12K_DBG_WMI,\n'
                r'\t\t   "WMI control connect pdev %u service 0x%x endpoints %d max-radios %d qmi-radios %d group-id %d wsi-index %u device-id %d wsi-controller %d\\n",\n'
                r'\t\t   pdev_idx, conn_req.service_id, ab->htc.wmi_ep_count,\n'
                r'\t\t   ab->hw_params->max_radios, ab->qmi.num_radios,\n'
                r'\t\t   ag ? ag->id : ATH12K_INVALID_GROUP_ID, ab->wsi_info.index,\n'
                r'\t\t   ab->device_id, wsi_controller);\n'
            ),
            # 3. Warning log in case of replacement failure, carrying complete WMI/WSI topology parameters
            (
                r'[ \t]*ath12k_warn\(ab,\s*"failed to connect to WMI CONTROL service status:\s*%d\\n",\s*status\);',
                r'\t\tath12k_warn(ab,\n'
                r'\t\t\t   "failed to connect WMI control pdev %u service 0x%x: %d (endpoints %d max-radios %d qmi-radios %d group-id %d wsi-index %u device-id %d wsi-controller %d)\\n",\n'
                r'\t\t\t   pdev_idx, conn_req.service_id, status,\n'
                r'\t\t\t   ab->htc.wmi_ep_count, ab->hw_params->max_radios,\n'
                r'\t\t\t   ab->qmi.num_radios,\n'
                r'\t\t\t   ag ? ag->id : ATH12K_INVALID_GROUP_ID,\n'
                r'\t\t\t   ab->wsi_info.index, ab->device_id, wsi_controller);'
            ),
        ],
    },
    {
        'tree': 'mac80211',
        'name': '910-wifi-ath12k-limit-WMI-endpoints-to-QMI-PHY-count',
        'filename': 'htc.c',
        'path_must_contain': ('mac80211', 'backports', 'drivers/net/wireless/ath/ath12k'),
        'parent_dir_exact': 'ath12k',
        'kind': 'regex',
        'replacements': [
            # Limit the number of WMI endpoints to no more than the number of PHY broadcasts in QMI
            (
                r'([ \t]*htc->wmi_ep_count\s*=\s*ab->hw_params->max_radios;\s*\n'
                r'[ \t]*break;\s*\n'
                r'[ \t]*\}\n)'
                r'(\n[ \t]*/\* setup our pseudo HTC control endpoint connection \*/)',

                r'\1'
                r'\tif (ab->qmi.num_radios > 0 && ab->qmi.num_radios != U8_MAX)\n'
                r'\t\thtc->wmi_ep_count = min_t(u8, htc->wmi_ep_count,\n'
                r'\t\t\t\t\t  ab->qmi.num_radios);\n'
                r'\2'
            ),
        ],
    },
    #{
    #    'tree': 'mac80211',
    #    'name': '111-wifi-ath12k-support-Wi-Fi-radar-direct-buffer-module',
    #    'filename': 'wmi.h',
    #    'path_must_contain': ('mac80211', 'backports', 'drivers/net/wireless/ath/ath12k'),
    #    'parent_dir_exact': 'ath12k',
    #    'kind': 'regex',
    #    'replacements': [
    #        # Add WMI_CONFIG_MODULE_WIFI_RADAR enumeration value to enum wmi_direct_buffer_module
    #        (
    #            r'([ \t]*WMI_DIRECT_BUF_CV_UPLOAD\s*=\s*2,?\n)',
    #            r'\1\tWMI_CONFIG_MODULE_WIFI_RADAR = 3,\n'
    #        ),
    #    ],
    #},
    {
        'tree': 'mac80211',
        'name': '400-wifi-ath12k-set-per-radio-MAC-address-from-DT',
        'filename': 'mac.c',
        'path_must_contain': ('mac80211', 'backports', 'drivers/net/wireless/ath/ath12k'),
        'parent_dir_exact': 'ath12k',
        'kind': 'regex',
        'replacements': [
            # 1. Header file reference area introduction <linux/of_net.h>
            (
                r'(#include <linux/etherdevice\.h>\n)',
                r'\1#include <linux/of_net.h>\n'
            ),
            # 2. Add struct mac_address *addresses to ath12k_mac_setup_iface_combinations;
            (
                r'(struct wiphy \*wiphy = ah->hw->wiphy;\n[ \t]*struct wiphy_radio \*radio;\n)',
                r'\1\tstruct mac_address *addresses;\n'
            ),
            # 3. Increase addresses memory allocation and update the goto abnormal jump label after radio allocation failure
            (
                r'([ \t]*/\* there are multiple radios \*/\n\n)'
                r'([ \t]*radio = [^;\n]+;\n'
                r'[ \t]*if \(!radio\) \{\n'
                r'[ \t]*ret = -ENOMEM;\n)'
                r'[ \t]*goto err_free_combinations;',

                r'\1\taddresses = kcalloc(ah->num_radio, sizeof(*addresses), GFP_KERNEL);\n'
                r'\tif (!addresses) {\n'
                r'\t\tret = -ENOMEM;\n'
                r'\t\tgoto err_free_combinations;\n'
                r'\t}\n\n'
                r'\2\n\t\tgoto err_free_addresses;'
            ),
            # 4. Copy the MAC address to the addresses array at the end of the for_each_ar loop
            (
                r'([ \t]*radio\[i\]\.n_iface_combinations = 1;\n)',
                r'\1\n\t\tether_addr_copy(addresses[i].addr, ar->mac_addr);\n'
            ),
            # 5. Set the addresses and n_addresses members of the wiphy structure
            (
                r'([ \t]*wiphy->n_radio = ah->num_radio;\n)',
                r'\1\n\twiphy->addresses = addresses;\n\twiphy->n_addresses = ah->num_radio;\n'
            ),
            # 6. Add kfree(addresses) to the error cleaning node
            (
                r'([ \t]*kfree\(radio\);\n\n)(err_free_combinations:)',
                r'\1err_free_addresses:\n\tkfree(addresses);\n\n\2'
            ),
            # 7. Read the MAC address from DT for a single Radio device in ath12k_mac_hw_register
            (
                r'([ \t]*ar->mac_addr\[4\] \+= ar->pdev_idx;\n'
                r'[ \t]*\}\n)',

                r'\1\n'
                r'\t\t/*\n'
                r'\t\t * In the ath12k-wsi binding each radio is its own device\n'
                r'\t\t * node, so a DT "mac-address" (e.g. an nvmem cell) on the\n'
                r'\t\t * node is this radio\'s. A chip backing several radios shares\n'
                r'\t\t * one node and can\'t express a per-radio address, so read DT\n'
                r'\t\t * only for single-radio chips; the rest keep the address\n'
                r'\t\t * derived above.\n'
                r'\t\t */\n'
                r'\t\tif (ar->ab->num_radios == 1)\n'
                r'\t\t\tof_get_mac_address(dev_of_node(ar->ab->dev), ar->mac_addr);\n'
            ),
            # 8. Remove the override settings for global ab->mac_addr under multiple radio scenarios
            (
                r'([ \t]*if \(i == 0\)\n[ \t]*mac_addr = ar->mac_addr;\n)'
                r'[ \t]*else\n[ \t]*mac_addr = ab->mac_addr;\n',

                r'\1'
            ),
        ],
    },
    {
        'tree': 'mac80211',
        'name': '701-wifi-ath12k-support-memory-type-10',
        'filename': 'qmi.c',
        'path_must_contain': ('mac80211', 'backports', 'drivers/net/wireless/ath/ath12k'),
        'parent_dir_exact': 'ath12k',
        'kind': 'regex',
        'replacements': [
            # Add support for No. 10 memory area type in QMI memory allocation switch-case
            (
                r'([ \t]*)case LPASS_SHARED_V01_REGION_TYPE:\n',
                r'\1case LPASS_SHARED_V01_REGION_TYPE:\n\1case 10:\n'
            ),
        ],
    },
    # ---- Generic hack, universal for all targets, fall into target/linux/generic/hack-6.18/ ----
    {
        'tree': 'kernel-generic',
        'name': '743-net-phy-realtek-add-rtl826x-led-support',
        'filename': 'realtek_main.c',
        'path_must_contain': ('drivers', 'net', 'phy', 'realtek'),
        'kind': 'regex',
        'replacements': [
            # 1. Insert LED register definition + 3 hook functions before realtek_drvs[] array declaration
            (
                r'static struct phy_driver realtek_drvs\[\] = \{',
 
                '/* Per-LED mode register pair: link-speed qualifier (L) and flags (H) */\n'
                '#define RTL826X_LED_L(n)\t\t(21 + (n) * 2)\n'
                '#define RTL826X_LED_L_100M\t\tBIT(8)\n'
                '#define RTL826X_LED_L_500M\t\tBIT(7)\n'
                '#define RTL826X_LED_L_1G\t\tBIT(6)\n'
                '#define RTL826X_LED_L_2P5G\t\tBIT(4)\n'
                '#define RTL826X_LED_L_5G\t\tBIT(2)\n'
                '#define RTL826X_LED_L_10G\t\tBIT(0)\n'
                '#define RTL826X_LED_L_LINK_MASK\t\t(RTL826X_LED_L_100M | \\\n'
                '\t\t\t\t\t RTL826X_LED_L_500M | \\\n'
                '\t\t\t\t\t RTL826X_LED_L_1G | \\\n'
                '\t\t\t\t\t RTL826X_LED_L_2P5G | \\\n'
                '\t\t\t\t\t RTL826X_LED_L_5G | \\\n'
                '\t\t\t\t\t RTL826X_LED_L_10G)\n'
                '\n'
                '#define RTL826X_LED_H(n)\t\t(22 + (n) * 2)\n'
                '#define RTL826X_LED_H_LINK_EN\t\tBIT(9)\n'
                '#define RTL826X_LED_H_TX_ACT\t\tBIT(3)\n'
                '#define RTL826X_LED_H_RX_ACT\t\tBIT(2)\n'
                '\n'
                '#define RTL826X_LED_NUM\t\t\t6\n'
                '\n'
                'static const unsigned long rtl826x_led_rules =\n'
                '\tBIT(TRIGGER_NETDEV_LINK) |\n'
                '\tBIT(TRIGGER_NETDEV_LINK_100) |\n'
                '\tBIT(TRIGGER_NETDEV_LINK_1000) |\n'
                '\tBIT(TRIGGER_NETDEV_LINK_2500) |\n'
                '\tBIT(TRIGGER_NETDEV_LINK_5000) |\n'
                '\tBIT(TRIGGER_NETDEV_LINK_10000) |\n'
                '\tBIT(TRIGGER_NETDEV_RX) |\n'
                '\tBIT(TRIGGER_NETDEV_TX);\n'
                '\n'
                'static int rtl826x_led_hw_is_supported(struct phy_device *phydev, u8 index,\n'
                '\t\t\t\t       unsigned long rules)\n'
                '{\n'
                '\tif (index >= RTL826X_LED_NUM)\n'
                '\t\treturn -EINVAL;\n'
                '\n'
                '\tif (rules & ~rtl826x_led_rules)\n'
                '\t\treturn -EOPNOTSUPP;\n'
                '\n'
                '\treturn 0;\n'
                '}\n'
                '\n'
                'static int rtl826x_led_hw_control_get(struct phy_device *phydev, u8 index,\n'
                '\t\t\t\t      unsigned long *rules)\n'
                '{\n'
                '\tint l, h;\n'
                '\n'
                '\tif (index >= RTL826X_LED_NUM)\n'
                '\t\treturn -EINVAL;\n'
                '\n'
                '\tl = phy_read_mmd(phydev, MDIO_MMD_VEND1, RTL826X_LED_L(index));\n'
                '\tif (l < 0)\n'
                '\t\treturn l;\n'
                '\n'
                '\th = phy_read_mmd(phydev, MDIO_MMD_VEND1, RTL826X_LED_H(index));\n'
                '\tif (h < 0)\n'
                '\t\treturn h;\n'
                '\n'
                '\t*rules = 0;\n'
                '\n'
                '\t/* Speed qualifiers only drive the LED with the link enable set */\n'
                '\tif (!(h & RTL826X_LED_H_LINK_EN)) {\n'
                '\t\tl = 0;\n'
                '\t} else if ((l & RTL826X_LED_L_LINK_MASK) == RTL826X_LED_L_LINK_MASK) {\n'
                '\t\t*rules |= BIT(TRIGGER_NETDEV_LINK);\n'
                '\t\tl = 0;\n'
                '\t}\n'
                '\n'
                '\tif (l & RTL826X_LED_L_100M)\n'
                '\t\t*rules |= BIT(TRIGGER_NETDEV_LINK_100);\n'
                '\tif (l & RTL826X_LED_L_1G)\n'
                '\t\t*rules |= BIT(TRIGGER_NETDEV_LINK_1000);\n'
                '\tif (l & RTL826X_LED_L_2P5G)\n'
                '\t\t*rules |= BIT(TRIGGER_NETDEV_LINK_2500);\n'
                '\tif (l & RTL826X_LED_L_5G)\n'
                '\t\t*rules |= BIT(TRIGGER_NETDEV_LINK_5000);\n'
                '\tif (l & RTL826X_LED_L_10G)\n'
                '\t\t*rules |= BIT(TRIGGER_NETDEV_LINK_10000);\n'
                '\n'
                '\tif (h & RTL826X_LED_H_RX_ACT)\n'
                '\t\t*rules |= BIT(TRIGGER_NETDEV_RX);\n'
                '\tif (h & RTL826X_LED_H_TX_ACT)\n'
                '\t\t*rules |= BIT(TRIGGER_NETDEV_TX);\n'
                '\n'
                '\treturn 0;\n'
                '}\n'
                '\n'
                'static int rtl826x_led_hw_control_set(struct phy_device *phydev, u8 index,\n'
                '\t\t\t\t      unsigned long rules)\n'
                '{\n'
                '\tu16 l = 0, h = 0;\n'
                '\tint ret;\n'
                '\n'
                '\tif (index >= RTL826X_LED_NUM)\n'
                '\t\treturn -EINVAL;\n'
                '\n'
                '\tif (rules & BIT(TRIGGER_NETDEV_LINK))\n'
                '\t\tl |= RTL826X_LED_L_LINK_MASK;\n'
                '\tif (rules & BIT(TRIGGER_NETDEV_LINK_100))\n'
                '\t\tl |= RTL826X_LED_L_100M;\n'
                '\tif (rules & BIT(TRIGGER_NETDEV_LINK_1000))\n'
                '\t\tl |= RTL826X_LED_L_1G;\n'
                '\tif (rules & BIT(TRIGGER_NETDEV_LINK_2500))\n'
                '\t\tl |= RTL826X_LED_L_2P5G;\n'
                '\tif (rules & BIT(TRIGGER_NETDEV_LINK_5000))\n'
                '\t\tl |= RTL826X_LED_L_5G;\n'
                '\tif (rules & BIT(TRIGGER_NETDEV_LINK_10000))\n'
                '\t\tl |= RTL826X_LED_L_10G;\n'
                '\n'
                '\t/* Link rules only light the LED with the enable flag set */\n'
                '\tif (l)\n'
                '\t\th |= RTL826X_LED_H_LINK_EN;\n'
                '\n'
                '\tif (rules & BIT(TRIGGER_NETDEV_RX))\n'
                '\t\th |= RTL826X_LED_H_RX_ACT;\n'
                '\tif (rules & BIT(TRIGGER_NETDEV_TX))\n'
                '\t\th |= RTL826X_LED_H_TX_ACT;\n'
                '\n'
                '\tret = phy_write_mmd(phydev, MDIO_MMD_VEND1, RTL826X_LED_L(index), l);\n'
                '\tif (ret < 0)\n'
                '\t\treturn ret;\n'
                '\n'
                '\treturn phy_write_mmd(phydev, MDIO_MMD_VEND1, RTL826X_LED_H(index), h);\n'
                '}\n'
                '\n'
                'static struct phy_driver realtek_drvs[] = {'
                # Note: Only replace here (Article 1 is expected to hit 1 time by default), because the array statement realtek_drvs[] should be unique in the file.
            ),
            # 2. Add LED hooks to every PHY driver entry that uses rtl826x_set_tunable.
            # There are currently 6 such entries upstream (RTL8254/8254B/8261BE/8261N/8264/8264B), 
            # which is expected to hit 6 times - if the number of hits is not equal to 6, it will be alerted,
            # instead of being covered up as a bug of "injuring multiple places by mistake".
            # In the future, if the upstream is added or deleted, this number should be checked accordingly.
            (
                r'([ \t]*\.get_tunable[ \t]*=[ \t]*rtl826x_get_tunable,\n)([ \t]*)(\.set_tunable[ \t]*=[ \t]*rtl826x_set_tunable,\n)',
                r'\1\2\3'
                r'\2.led_hw_is_supported = rtl826x_led_hw_is_supported,\n'
                r'\2.led_hw_control_get = rtl826x_led_hw_control_get,\n'
                r'\2.led_hw_control_set = rtl826x_led_hw_control_set,\n',
                6,
            ),
        ],
    },
    # ---- hostapd tree ----
    {
        'tree': 'hostapd',
        'name': '980-AP-keep_configured_width_on_5G_6G-if_20M_40M_scan_fails',
        'filename': 'hw_features.c',
        'path_must_contain': ('src', 'ap'),
        'kind': 'regex',
        'replacements': [
            (
                r'(?P<i>[ \t]*)wpa_printf\(MSG_DEBUG,\s*\n\s*"Failed to request a scan in device, bringing up in HT20 mode"\);',
                r'\g<i>/*\n'
                r'\g<i> * On 5/6 GHz the scan can only make us swap the primary and secondary\n'
                r'\g<i> * channel (check_40mhz_5g() never disallows 40 MHz there), so without\n'
                r'\g<i> * it keep the configured width, as noscan=1 does.\n'
                r'\g<i> */\n'
                r'\g<i>if (iface->current_mode->mode == HOSTAPD_MODE_IEEE80211A) {\n'
                r'\g<i>\twpa_printf(MSG_INFO,\n'
                r'\g<i>\t\t   "Failed to request a scan of neighboring BSSes, keeping the configured channel width");\n'
                r'\g<i>\thostapd_setup_interface_complete(iface, 0);\n'
                r'\g<i>\treturn;\n'
                r'\g<i>}\n\n'
                r'\g<i>wpa_printf(MSG_DEBUG,\n'
                r'\g<i>\t   "Failed to request a scan in device, bringing up in HT20 mode");',
                1,
            ),
        ],
    },
]
