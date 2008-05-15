import os
import sys
import commands
import glob

import utilities

def change_v1_to_v2(v1_filename):
    v1 = open(v1_filename, 'r').read()
    v2 = v1.replace('1.0','3.0')
    f = open(v1_filename, 'w')
    f.write(v2)
    f.close()

def generate_2(v1_directory, v2_directory, key_file):
    assert(os.path.exists('%s' % v1_directory))

    print commands.getoutput('rm -rf %s' % v2_directory)
    assert(not os.path.exists('%s' % v2_directory))

    print commands.getoutput('cp -rf %s %s' % (v1_directory, v2_directory))
    assert(os.path.exists('%s' % v2_directory))

    assert(os.path.exists('%s/%s' % (v2_directory, key_file)))
    change_v1_to_v2('%s/%s' % (v2_directory, key_file))
    
    print commands.getoutput('tar cf %s.tar %s' % (v2_directory, v2_directory))
    assert(os.path.exists('%s.tar' % v2_directory))

    assert(os.path.exists('%s' % v2_directory))
    print commands.getoutput('rm -rf %s' % v2_directory)
    assert(not os.path.exists('%s' % v2_directory))

    print commands.getoutput('gzip %s.tar' % v2_directory)
    assert(os.path.exists('%s.tar.gz' % v2_directory))

    print commands.getoutput('mv %s.tar.gz /var/www/' % v2_directory)
    assert(os.path.exists('/var/www/%s.tar.gz' % v2_directory))

generate_2('game-1.0', 'game-2.0', 'game.py')
#generate_2('selfupdater', 'selfupdater-3.0', 'selfupdater.py')

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
