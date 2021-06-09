/*************************************************************************
 * Copyright (c) 2011 AT&T Intellectual Property 
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors: Details at https://graphviz.org
 *************************************************************************/

#include <glcomp/glcompimage.h>
#include <glcomp/glcompfont.h>
#include <glcomp/glcompset.h>
#include <glcomp/glutils.h>
#include <glcomp/glcomptexture.h>
#include <common/memory.h>

glCompImage *glCompImageNew(glCompObj * par, GLfloat x, GLfloat y)
{
    glCompImage *p;
    p = NEW(glCompImage);
    glCompInitCommon((glCompObj *) p, par, x, y);
    p->objType = glImageObj;
    //typedef enum {glPanelObj,glbuttonObj,glLabelObj,glImageObj}glObjType;

    p->objType = glImageObj;
    p->stretch = 0;
#if 0
    p->pngFile = (char *) 0;
#endif
    p->texture = NULL;
    p->common.functions.draw = glCompImageDraw;
    return p;
}

/* glCompImageNewFile:
 * Creates image from given input file.
 * At present, we assume png input.
 * Return 0 on failure.
 */
glCompImage *glCompImageNewFile (glCompObj * par, GLfloat x, GLfloat y, char* imgfile, int is2D)
{
    int imageWidth, imageHeight;
    unsigned char *data = glCompLoadPng (imgfile, &imageWidth, &imageHeight);
    glCompImage *p;

    if (!data) return NULL;
    p = glCompImageNew (par, x, y);
    if (!glCompImageLoad (p, data, imageWidth, imageHeight, is2D)) {
	glCompImageDelete (p);
	return NULL;
    }
    return p;
}

void glCompImageDelete(glCompImage * p)
{
    glCompEmptyCommon(&p->common);
#if 0
    if (p->pngFile)
	free(p->pngFile);
#endif
    if (p->texture)
	glCompDeleteTexture(p->texture);
    free(p);
}

int glCompImageLoad(glCompImage * i, unsigned char *data, int width,
		    int height,int is2D)
{
    if (data != NULL) {		/*valid image data */
	glCompDeleteTexture(i->texture);
	i->texture =
	    glCompSetAddNewTexImage(i->common.compset, width, height, data,
				    is2D);
	if (i->texture) {
	    i->common.width = width;
	    i->common.height = height;
	    return 1;
	}

    }
    return 0;
}



int glCompImageLoadPng(glCompImage * i, char *pngFile,int is2D)
{
    int imageWidth, imageHeight;
    unsigned char *data;
    data = glCompLoadPng (pngFile, &imageWidth, &imageHeight);
    return glCompImageLoad(i, data, imageWidth, imageHeight,is2D);
}

#if 0
int glCompImageLoadRaw(glCompSet * s, glCompImage * i, char *rawFile,int is2D)
{
    int imageWidth, imageHeight;
    unsigned char *data;
    data = glCompLoadPng (rawFile, &imageWidth, &imageHeight);
    return glCompImageLoad(i, data, imageWidth, imageHeight,is2D);
}
#endif

void glCompImageDraw(void *obj)
{
    glCompImage *p = (glCompImage *) obj;
    glCompCommon ref = p->common;
    GLfloat w,h,d;

    glCompCalcWidget((glCompCommon *) p->common.parent, &p->common, &ref);
    if (!p->common.visible)
	return;
    if (!p->texture)
	return;

    if(p->texture->id <=0)
    {
	glRasterPos2f(ref.pos.x, ref.pos.y);
	glDrawPixels(p->texture->width, p->texture->height, GL_RGBA,GL_UNSIGNED_BYTE, p->texture->data);
    }
    else
    {
#if 0
	w=ref.width;
	h=ref.height;
#endif
	w = p->width;
	h = p->height;
	d=(GLfloat)p->common.layer* (GLfloat)GLCOMPSET_BEVEL_DIFF;
	glDisable(GL_BLEND);
	glEnable(GL_TEXTURE_2D);
	glTexEnvf (GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL);
	glBindTexture(GL_TEXTURE_2D,p->texture->id);
	glBegin(GL_QUADS);
		glTexCoord2d(0.0f, 1.0f);glVertex3d(ref.pos.x,ref.pos.y,d);
		glTexCoord2d(1.0f, 1.0f);glVertex3d(ref.pos.x+w,ref.pos.y,d);
		glTexCoord2d(1.0f, 0.0f);glVertex3d(ref.pos.x+w,ref.pos.y+h,d);
		glTexCoord2d(0.0f, 0.0f);glVertex3d(ref.pos.x,ref.pos.y+h,d);
	glEnd();


	glDisable(GL_TEXTURE_2D);
	glEnable(GL_BLEND);
    }

}
