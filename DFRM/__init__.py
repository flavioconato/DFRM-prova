# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DFRM
                                 A QGIS plugin
 DFRM interface
                             -------------------
        begin                : 2019-08-07
        copyright            : (C) 2019 by Greg's Lab
        email                : carlo.gregoretti@unipd.it
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DFRM class from file DFRM.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .dfrm import DFRM
    return DFRM(iface)
