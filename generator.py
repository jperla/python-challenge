import os
import sys
import commands

def change_v1_to_v2(v1):
    """
    >>> v1 = 'This is version 1.0 of the game'
    >>> print change_v1_to_v2(v1)
    This is version 2.0 of the game
    """
    v2 = v1.replace('1.0','2.0')
    return v2

def generate_2(v1_filename):
    assert(os.path.exists('%s' % v1_filename))

    v1 = open(v1_filename, 'r').read()

    v2 = change_v1_to_v2(v1)
    v2_filename = 'url/' + v1_filename+'_2'

    v2_file = open(v2_filename, 'w')
    v2_file.write(v2)
    v2_file.close()

    print commands.getoutput('tar cf %s.tar %s' % (v2_filename, v2_filename))
    print commands.getoutput('chmod 777 %s.tar' % v2_filename)
    print commands.getoutput('sudo mv %s.tar /var/www/' % v2_filename)
    print commands.getoutput('rm %s' % v2_filename)

    assert(os.path.exists('%s' % v1_filename))

generate_2('game.py')

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
