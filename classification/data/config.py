"""
Configuration of various things.
"""

# The input features to use.
# noinspection SpellCheckingInspection
features = ["c_pkts_all", "c_rst_cnt", "c_ack_cnt", "c_ack_cnt_p", "c_bytes_uniq", "c_pkts_data", "c_bytes_all",
            "c_pkts_retx", "c_bytes_retx", "c_pkts_ooo", "c_syn_cnt", "c_fin_cnt", "s_pkts_all", "s_rst_cnt",
            "s_ack_cnt", "s_ack_cnt_p", "s_bytes_uniq", "s_pkts_data", "s_bytes_all", "s_pkts_retx", "s_bytes_retx",
            "s_pkts_ooo", "s_syn_cnt", "s_fin_cnt", "durat", "c_first", "s_first", "c_last", "s_last", "c_first_ack",
            "s_first_ack", "complete"]
