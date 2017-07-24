from distutils.core import setup


setup(name='BitEx', version='1.1.4', author='Nils Diefenbach',
      author_email='23okrs20+pypi@mykolab.com',
      url="https://github.com/nlsdfnbch/bitex.git",
      packages=['bitex', 'bitex.api', 'bitex.api.WSS', 'bitex.api.REST',
                'bitex.interfaces', 'bitex.formatters'],
      install_requires=['requests', 'websocket-client', 'autobahn',
                        'pusherclient'],
      description='Python3-based API Framework for Crypto Exchanges',
      license='MIT',  classifiers=['Development Status :: 4 - Beta',
                                   'Intended Audience :: Developers'],
      )

