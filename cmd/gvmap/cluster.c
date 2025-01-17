/*************************************************************************
 * Copyright (c) 2011 AT&T Intellectual Property 
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors: Details at https://graphviz.org
 *************************************************************************/

#include "config.h"
#include "../tools/openFile.h"
#include <cgraph/unreachable.h>
#include <stdio.h>
#include <stdlib.h>
#define STANDALONE
#include <sparse/general.h>
#include <sparse/QuadTree.h>
#include <time.h>
#include <sparse/SparseMatrix.h>
#include <getopt.h>
#include <string.h>
#include "make_map.h"
#include <sfdpgen/spring_electrical.h>
#include <sfdpgen/post_process.h>
#include <neatogen/overlap.h>
#include <sparse/clustering.h>
#include <cgraph/ingraphs.h>
#include <sparse/DotIO.h>
#include <sparse/colorutil.h>

typedef struct {
  FILE* outfp;
  char** infiles;
  int maxcluster;
  int clustering_method;
} opts_t;

static const char usestr[] =
"    -C k - generate no more than k clusters (0)\n\
       0 : no limit\n\
    -c k - use clustering method k (0)\n\
       0 : use modularity\n\
       1 : use modularity quality\n\
    -o <outfile> - output file (stdout)\n\
    -v   - verbose mode\n\
    -?   - print usage\n";

static void usage(char* cmd, int eval)
{
    fprintf(stderr, "Usage: %s <options> graphfile\n", cmd);
    fputs (usestr, stderr);
    graphviz_exit(eval);
}

static void init(int argc, char *argv[], opts_t* opts) {
  char* cmd = argv[0];
  int c;
  int v;

  opts->maxcluster = 0;
  opts->outfp = stdout;
  Verbose = 0;

  opts->clustering_method =  CLUSTERING_MODULARITY;
  while ((c = getopt(argc, argv, ":vC:c:o:?")) != -1) {
    switch (c) {
    case 'c':
      if (sscanf(optarg, "%d", &v) == 0 || v < 0) {
	usage(cmd,1);
      }
      else opts->clustering_method = v;
      break;
    case 'C':
      if (sscanf(optarg, "%d", &v) == 0 || v < 0) {
	usage(cmd,1);
      }
      else opts->maxcluster = v;
      break;
    case 'o':
      opts->outfp = openFile(cmd, optarg, "w");
      break;
    case 'v':
      Verbose = 1;
      break;
    case '?':
      if (optopt == '\0' || optopt == '?')
	usage(cmd, 0);
      else {
	fprintf(stderr, " option -%c unrecognized\n",
		optopt);
	usage(cmd, 1);
      }
      break;
    default:
      UNREACHABLE();
    }
  }

  argv += optind;
  argc -= optind;
  if (argc)
    opts->infiles = argv;
  else
    opts->infiles = NULL;
}

static void clusterGraph (Agraph_t* g, int maxcluster, int clustering_method){
  initDotIO(g);
  attached_clustering(g, maxcluster, clustering_method);
}

int main(int argc, char *argv[])
{
  Agraph_t *g = 0, *prevg = 0;
  ingraph_state ig;
  opts_t opts;

  init(argc, argv, &opts);

  newIngraph(&ig, opts.infiles);

  while ((g = nextGraph (&ig)) != 0) {
    if (prevg) agclose (prevg);
    clusterGraph (g, opts.maxcluster, opts.clustering_method);
    agwrite(g, opts.outfp);
    prevg = g;
  }

  graphviz_exit(0);
}
