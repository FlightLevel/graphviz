/*************************************************************************
 * Copyright (c) 2011 AT&T Intellectual Property
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors: Details at https://graphviz.org
 *************************************************************************/

#include <gvc/gvplugin.h>

extern gvplugin_installed_t gvdevice_lasi_types[];
extern gvplugin_installed_t gvrender_lasi_types[];
extern gvplugin_installed_t gvloadimage_lasi_types[];

static gvplugin_api_t apis[] = {
    {API_device, gvdevice_lasi_types},
    {API_render, gvrender_lasi_types},
    {API_loadimage, gvloadimage_lasi_types},
    {(api_t)0, 0},
};

gvplugin_library_t gvplugin_lasi_LTX_library = {"lasi", apis};
