import sys
if sys.version_info < (3, 3):
    print("[IDACode] Python 2.7 is not (yet) supported, vote at https://github.com/ioncodes/idacode/issues/3")
    sys.exit()

import idacode_utils.plugin as plugin

def PLUGIN_ENTRY():
    return plugin.IDACode()