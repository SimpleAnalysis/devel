#!/usr/bin/python
# -*- coding:utf-8 -*-

# Copyright (c) 2015 yu.liu <showmove@qq.com>
# All rights reserved

# pylint:disable-all

from lawfirm_model import *


class ot_agency(agencydataModel, Base_to):

    """  原始库  """


class ot_agency_old(agencyModel, Base_to):

    """  中间库  """


class ot_agency_bd_old(bdoldmodel, Base_to):

    """  中间库  """


class ot_agency_info(AgencyInfoModel, Base_to):

    """  INFO库  """


class ot_lawyer_bases(LawyerModel, Base_to):

    """  律师库中间库 """


class ot_lawyer_old(LawyerModel, Base_to):

    """  律师库中间库 """


class ot_agency_lawfirm_major(AgencyLawfirmModel, Base_to):

    """  详情表   """


class ot_agency_main(AgencyMainModel, Base_to):

    """  成果库  """


class ot_lawfirm_base(AgencyMainModel, Base_to):

    """  成果库  """


class ot_agency_court(AreaModel, Base_to):

    """  法院库 """
