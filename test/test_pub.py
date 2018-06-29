#!/usr/bin/python
 # -*- coding: utf-8 -*-

import unittest
from nose.tools import nottest
from nose.tools import assert_equals
from nose.tools import assert_not_equals
from nose.tools import assert_true
import requests
from ddt import ddt, data
import requests_cache

from software import Software
from app import libraries_to_mum

requests_cache.install_cache('my_requests_cache', expire_after=60*60*24*7)  # expire_after is in seconds

# run it like this:
# nosetests --processes=10 test/

test_urls = [
    ("http://cnn.com", "", u'Anon, CNN - Breaking News, Latest News and Videos. Available at: http://cnn.com.'),
    ("https://github.com/pvlib/pvlib-python", "10.5281/zenodo.50141", "Holmgren, W. et al., 2016. Pvlib-python: 0.3.1. Available at: https://doi.org/10.5281/zenodo.50141."),
    ("https://github.com/gcowan/hyperk", "10.5281/zenodo.160400", "Cowan, G., 2016. Gcowan/Hyperk: Mcp Data Processing Code. Available at: https://doi.org/10.5281/zenodo.160400."),
    ("https://github.com/NSLS-II-XPD/xpdView", "10.5281/zenodo.60479", "Duff, C. & Kaming-Thanassi, J., 2016. XpdView: xpdView initial release. Available at: https://doi.org/10.5281/zenodo.60479."),
    ("https://github.com/impactstory/depsy", "", "Anon, GitHub - Impactstory/depsy: Track the impact of research software.. Available at: https://github.com/impactstory/depsy."),
    ("https://github.com/abianchetti/blick", "", u"Bianchetti, A., 2012. <i>Determinación del diámetro pupilar ocular en tiempo real</i>."),
    ("https://github.com/jasonpriem/FeedVis", "", u"Priem, J., 2011. FeedVis. Available at: https://github.com/jasonpriem/FeedVis."),
    ("https://github.com/vahtras/loprop", "", u'Vahtras, O., 2014. Loprop For Dalton. Available at: https://doi.org/10.5281/zenodo.13276.'),
    ("https://github.com/cvitolo/r_BigDataAnalytics", "", u'Vitolo, C., 2015. R_Bigdataanalytics V.0.0.1. Available at: https://doi.org/10.5281/zenodo.15722.'),
    ("https://github.com/nicholasricci/DDM_Framework", "", u"Marzolla, M., D'Angelo, G. & Mandrioli, M., 2013. A Parallel Data Distribution Management Algorithm."),
    ("http://yt-project.org", "", u"Turk, M.J. et al., 2010. Yt: A Multi-Code Analysis Toolkit For Astrophysical Simulation Data. <i>The Astrophysical Journal Supplement Series</i>, 192(1), p.9. Available at: https://doi.org/10.1088/0067-0049/192/1/9."),
    ("https://github.com/dfm/emcee", "", u'Foreman-Mackey, D. et al., 2013. emcee: The MCMC Hammer. <i>Publications of the Astronomical Society of the Pacific</i>, 125(925), pp.306\u2013312. Available at: https://doi.org/10.1086/670067.'),
    ("https://github.com/robintw/Py6S", "", u'Wilson, R.T., 2013. Py6S: A Python interface to the 6S radiative transfer model. <i>Computers & Geosciences</i>, 51, pp.166–171. Available at: https://doi.org/10.1016/j.cageo.2012.08.002.'),
    ("http://fftw.org/", "", u'Frigo, M. & Johnson, S.G., 2005. The Design and Implementation of FFTW3. <i>Proceedings of the IEEE</i>, 93(2), pp.216–231. Available at: https://doi.org/10.1109/jproc.2004.840301.'),
    ("www.simvascular.org", "", u' 2015. SimVascular. Available at: https://github.com/SimVascular/SimVascular.'),
    ("arXiv:1802.02689", "", u'Borgman, C., Scharnhorst, A. & Golshan, M., 2018. Digital Data Archives as Knowledge Infrastructures: Mediating Data Sharing and Reuse. <i>arXiv</i>. Available at: http://arxiv.org/abs/1802.02689v1.'),
    ("https://bioconductor.org/packages/release/bioc/html/edgeR.html", "", u'Yunshun Chen <Yuchen@Wehi.Edu.Au>, A., Davis McCarthy <Dmccarthy@Wehi.Edu.Au>, Xiaobei Zhou <Xiaobei.Zhou@Uzh.Ch>, Mark Robinson<Mark.Robinson@Imls.Uzh.Ch>, Gordon Smyth <Smyth@Wehi.Edu.Au>, 2017. edgeR. Available at: https://doi.org/10.18129/b9.bioc.edger.')
    ]

@ddt
class MyTestCase(unittest.TestCase):
    _multiprocess_can_split_ = True

    @data(*test_urls)
    def test_the_urls(self, test_data):
        (url, doi, expected) = test_data
        my_software = Software(url)
        my_software.find_metadata()
        assert_equals(my_software.citation_plain, expected)

    @data(*test_urls)
    def test_the_dois(self, test_data):
        (url, doi, expected) = test_data
        if doi:
            my_software = Software(doi)
            my_software.find_metadata()
            assert_equals(my_software.citation_plain, expected)
