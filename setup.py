from setuptools import setup, find_packages



setup(name = 'django-visithistory',
      version = '0.1',
      description = 'Logs the visited websites, and allows get them later. Uses django cache system',
      author = 'Leander Hanwald',
      author_email = 'shockflash@web.de',

      url = 'https://github.com/shockflash/visithistory/',
      download_url = 'https://github.com/shockflash/visithistory/tarball/master',

      packages = find_packages(),

      license = 'BSD',

      classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      )
