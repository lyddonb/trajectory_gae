from distutils.core import setup

setup(
    name="trajectory",
    version="0.0.1",
    author="Beau Lyddon",
    author_email="lyddonb@gmail.com",
    packages=['trajectory', 'trajectory.providers', 'trajectory_web'],
    package_dir={'trajectory': 'trajectory',
                 'trajectory_web': 'trajectory_web'},
    package_data={'trajectory_web':
                  ['templates/*.html', 'templates/requests/*.html']},
    scripts=[],
    url='',
    license="LICENSE",
    description="Throw some trajectory into your GAE.",
    long_description="",
)
