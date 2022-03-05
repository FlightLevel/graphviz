#!/usr/bin/env python3

"""
validate formatting of C/C++ files

This script is deliberately a fairly simple-stupid translation of what would
otherwise be some steps described in awkward YAML in
../.gitlab-ci.yml:lint_clang_format.
"""

import difflib
from pathlib import Path
import subprocess
import sys

# TODO: files that are not yet compliant
EXCLUDE = (
  "cmd/dot/dot.c",
  "cmd/dot/dot_builtins.c",
  "cmd/dot/no_builtins.c",
  "cmd/dotty/mswin32/dotty.c",
  "cmd/edgepaint/edgepaintmain.c",
  "cmd/gvedit/csettings.cpp",
  "cmd/gvedit/csettings.h",
  "cmd/gvedit/imageviewer.cpp",
  "cmd/gvedit/imageviewer.h",
  "cmd/gvedit/main.cpp",
  "cmd/gvedit/mainwindow.cpp",
  "cmd/gvedit/mainwindow.h",
  "cmd/gvedit/mdichild.cpp",
  "cmd/gvedit/mdichild.h",
  "cmd/gvedit/ui_settings.h",
  "cmd/gvmap/cluster.c",
  "cmd/gvmap/country_graph_coloring.c",
  "cmd/gvmap/country_graph_coloring.h",
  "cmd/gvmap/gvmap.c",
  "cmd/gvmap/make_map.c",
  "cmd/gvmap/make_map.h",
  "cmd/gvmap/power.c",
  "cmd/gvmap/power.h",
  "cmd/gvpr/gvprmain.c",
  "cmd/lefty/aix_mods/common.h",
  "cmd/lefty/aix_mods/exec.c",
  "cmd/lefty/aix_mods/tbl.c",
  "cmd/lefty/code.c",
  "cmd/lefty/code.h",
  "cmd/lefty/common.c",
  "cmd/lefty/common.h",
  "cmd/lefty/cs2l/cs2l.c",
  "cmd/lefty/cs2l/cs2l.h",
  "cmd/lefty/display.c",
  "cmd/lefty/display.h",
  "cmd/lefty/dot2l/dot2l.c",
  "cmd/lefty/dot2l/dot2l.h",
  "cmd/lefty/dot2l/dotlex.c",
  "cmd/lefty/dot2l/dottrie.c",
  "cmd/lefty/dot2l/triefa.c",
  "cmd/lefty/dot2l/triefa.h",
  "cmd/lefty/exec.c",
  "cmd/lefty/exec.h",
  "cmd/lefty/g.c",
  "cmd/lefty/g.h",
  "cmd/lefty/gfxview.c",
  "cmd/lefty/gfxview.h",
  "cmd/lefty/internal.c",
  "cmd/lefty/internal.h",
  "cmd/lefty/lefty.c",
  "cmd/lefty/leftyio.h",
  "cmd/lefty/lex.c",
  "cmd/lefty/lex.h",
  "cmd/lefty/mem.c",
  "cmd/lefty/mem.h",
  "cmd/lefty/os/mswin32/io.c",
  "cmd/lefty/os/unix/io.c",
  "cmd/lefty/parse.c",
  "cmd/lefty/parse.h",
  "cmd/lefty/str.c",
  "cmd/lefty/str.h",
  "cmd/lefty/tbl.c",
  "cmd/lefty/tbl.h",
  "cmd/lefty/txtview.c",
  "cmd/lefty/txtview.h",
  "cmd/lefty/ws/gtk/garray.c",
  "cmd/lefty/ws/gtk/gbutton.c",
  "cmd/lefty/ws/gtk/gcanvas.c",
  "cmd/lefty/ws/gtk/gcommon.c",
  "cmd/lefty/ws/gtk/gcommon.h",
  "cmd/lefty/ws/gtk/glabel.c",
  "cmd/lefty/ws/gtk/gmenu.c",
  "cmd/lefty/ws/gtk/gpcanvas.c",
  "cmd/lefty/ws/gtk/gquery.c",
  "cmd/lefty/ws/gtk/gscroll.c",
  "cmd/lefty/ws/gtk/gtext.c",
  "cmd/lefty/ws/gtk/gview.c",
  "cmd/lefty/ws/mswin32/garray.c",
  "cmd/lefty/ws/mswin32/gbutton.c",
  "cmd/lefty/ws/mswin32/gcanvas.c",
  "cmd/lefty/ws/mswin32/gcommon.c",
  "cmd/lefty/ws/mswin32/gcommon.h",
  "cmd/lefty/ws/mswin32/glabel.c",
  "cmd/lefty/ws/mswin32/gmenu.c",
  "cmd/lefty/ws/mswin32/gpcanvas.c",
  "cmd/lefty/ws/mswin32/gquery.c",
  "cmd/lefty/ws/mswin32/gscroll.c",
  "cmd/lefty/ws/mswin32/gtext.c",
  "cmd/lefty/ws/mswin32/gview.c",
  "cmd/lefty/ws/mswin32/resource.h",
  "cmd/lefty/ws/none/garray.c",
  "cmd/lefty/ws/none/gbutton.c",
  "cmd/lefty/ws/none/gcanvas.c",
  "cmd/lefty/ws/none/gcommon.c",
  "cmd/lefty/ws/none/gcommon.h",
  "cmd/lefty/ws/none/glabel.c",
  "cmd/lefty/ws/none/gmenu.c",
  "cmd/lefty/ws/none/gpcanvas.c",
  "cmd/lefty/ws/none/gquery.c",
  "cmd/lefty/ws/none/gscroll.c",
  "cmd/lefty/ws/none/gtext.c",
  "cmd/lefty/ws/none/gview.c",
  "cmd/lefty/ws/x11/garray.c",
  "cmd/lefty/ws/x11/gbutton.c",
  "cmd/lefty/ws/x11/gcanvas.c",
  "cmd/lefty/ws/x11/gcommon.c",
  "cmd/lefty/ws/x11/gcommon.h",
  "cmd/lefty/ws/x11/glabel.c",
  "cmd/lefty/ws/x11/gmenu.c",
  "cmd/lefty/ws/x11/gpcanvas.c",
  "cmd/lefty/ws/x11/gquery.c",
  "cmd/lefty/ws/x11/gscroll.c",
  "cmd/lefty/ws/x11/gtext.c",
  "cmd/lefty/ws/x11/gview.c",
  "cmd/lefty/ws/x11/libfilereq/Dir.c",
  "cmd/lefty/ws/x11/libfilereq/Draw.c",
  "cmd/lefty/ws/x11/libfilereq/Path.c",
  "cmd/lefty/ws/x11/libfilereq/SF.h",
  "cmd/lefty/ws/x11/libfilereq/SFDecls.h",
  "cmd/lefty/ws/x11/libfilereq/SFinternal.h",
  "cmd/lefty/ws/x11/libfilereq/SelFile.c",
  "cmd/lefty/ws/x11/libfilereq/xstat.h",
  "cmd/lneato/mswin32/lneato.c",
  "cmd/mingle/minglemain.cpp",
  "cmd/smyrna/arcball.c",
  "cmd/smyrna/arcball.h",
  "cmd/smyrna/draw.c",
  "cmd/smyrna/draw.h",
  "cmd/smyrna/glexpose.c",
  "cmd/smyrna/glexpose.h",
  "cmd/smyrna/glmotion.c",
  "cmd/smyrna/glmotion.h",
  "cmd/smyrna/gltemplate.c",
  "cmd/smyrna/gltemplate.h",
  "cmd/smyrna/glutrender.c",
  "cmd/smyrna/glutrender.h",
  "cmd/smyrna/gui/appmouse.c",
  "cmd/smyrna/gui/appmouse.h",
  "cmd/smyrna/gui/callbacks.c",
  "cmd/smyrna/gui/callbacks.h",
  "cmd/smyrna/gui/datalistcallbacks.c",
  "cmd/smyrna/gui/datalistcallbacks.h",
  "cmd/smyrna/gui/frmobjectui.c",
  "cmd/smyrna/gui/frmobjectui.h",
  "cmd/smyrna/gui/glcompui.c",
  "cmd/smyrna/gui/glcompui.h",
  "cmd/smyrna/gui/gui.c",
  "cmd/smyrna/gui/gui.h",
  "cmd/smyrna/gui/menucallbacks.c",
  "cmd/smyrna/gui/menucallbacks.h",
  "cmd/smyrna/gui/toolboxcallbacks.c",
  "cmd/smyrna/gui/toolboxcallbacks.h",
  "cmd/smyrna/gui/topviewsettings.c",
  "cmd/smyrna/gui/topviewsettings.h",
  "cmd/smyrna/gvprpipe.c",
  "cmd/smyrna/gvprpipe.h",
  "cmd/smyrna/hier.c",
  "cmd/smyrna/hier.h",
  "cmd/smyrna/hotkeymap.c",
  "cmd/smyrna/hotkeymap.h",
  "cmd/smyrna/main.c",
  "cmd/smyrna/polytess.c",
  "cmd/smyrna/polytess.h",
  "cmd/smyrna/selectionfuncs.c",
  "cmd/smyrna/selectionfuncs.h",
  "cmd/smyrna/smyrna_utils.c",
  "cmd/smyrna/smyrna_utils.h",
  "cmd/smyrna/smyrnadefs.h",
  "cmd/smyrna/support.h",
  "cmd/smyrna/topfisheyeview.c",
  "cmd/smyrna/topfisheyeview.h",
  "cmd/smyrna/topviewfuncs.c",
  "cmd/smyrna/topviewfuncs.h",
  "cmd/smyrna/tvnodes.c",
  "cmd/smyrna/tvnodes.h",
  "cmd/smyrna/viewport.c",
  "cmd/smyrna/viewport.h",
  "cmd/smyrna/viewportcamera.c",
  "cmd/smyrna/viewportcamera.h",
  "cmd/tools/acyclic.c",
  "cmd/tools/bcomps.c",
  "cmd/tools/ccomps.c",
  "cmd/tools/colortbl.h",
  "cmd/tools/colxlate.c",
  "cmd/tools/convert.h",
  "cmd/tools/cvtgxl.c",
  "cmd/tools/dijkstra.c",
  "cmd/tools/gc.c",
  "cmd/tools/gml2gv.c",
  "cmd/tools/gml2gv.h",
  "cmd/tools/graph_generator.c",
  "cmd/tools/graph_generator.h",
  "cmd/tools/graphml2gv.c",
  "cmd/tools/gv2gml.c",
  "cmd/tools/gv2gxl.c",
  "cmd/tools/gvcolor.c",
  "cmd/tools/gvgen.c",
  "cmd/tools/gvpack.c",
  "cmd/tools/gxl2gv.c",
  "cmd/tools/matrix_market.c",
  "cmd/tools/matrix_market.h",
  "cmd/tools/mm2gv.c",
  "cmd/tools/mmio.c",
  "cmd/tools/mmio.h",
  "cmd/tools/nop.c",
  "cmd/tools/sccmap.c",
  "cmd/tools/tred.c",
  "cmd/tools/unflatten.c",
  "contrib/diffimg/diffimg.c",
  "contrib/pangotest/pangotest.c",
  "contrib/prune/generic_list.c",
  "contrib/prune/generic_list.h",
  "contrib/prune/prune.c",
  "doc/libgraph/agmemread.c",
  "doc/libgraph/sccmap.c",
  "lib/ast/ast.h",
  "lib/ast/chresc.c",
  "lib/ast/chrtoi.c",
  "lib/ast/compat_unistd.h",
  "lib/ast/error.c",
  "lib/ast/error.h",
  "lib/ast/fmtbuf.c",
  "lib/ast/fmtesc.c",
  "lib/ast/hashkey.h",
  "lib/ast/pathaccess.c",
  "lib/ast/pathcanon.c",
  "lib/ast/pathcat.c",
  "lib/ast/pathfind.c",
  "lib/ast/pathgetlink.c",
  "lib/ast/pathpath.c",
  "lib/ast/sfstr.h",
  "lib/ast/strcopy.c",
  "lib/ast/stresc.c",
  "lib/ast/strmatch.c",
  "lib/cdt/cdt.h",
  "lib/cdt/dtclose.c",
  "lib/cdt/dtdisc.c",
  "lib/cdt/dtextract.c",
  "lib/cdt/dtflatten.c",
  "lib/cdt/dthash.c",
  "lib/cdt/dthdr.h",
  "lib/cdt/dtlist.c",
  "lib/cdt/dtmethod.c",
  "lib/cdt/dtopen.c",
  "lib/cdt/dtrenew.c",
  "lib/cdt/dtrestore.c",
  "lib/cdt/dtsize.c",
  "lib/cdt/dtstat.c",
  "lib/cdt/dtstrhash.c",
  "lib/cdt/dttree.c",
  "lib/cdt/dtview.c",
  "lib/cdt/dtwalk.c",
  "lib/cgraph/agerror.c",
  "lib/cgraph/agxbuf.c",
  "lib/cgraph/agxbuf.h",
  "lib/cgraph/apply.c",
  "lib/cgraph/attr.c",
  "lib/cgraph/cghdr.h",
  "lib/cgraph/cgraph.h",
  "lib/cgraph/cmpnd.c",
  "lib/cgraph/edge.c",
  "lib/cgraph/flatten.c",
  "lib/cgraph/graph.c",
  "lib/cgraph/id.c",
  "lib/cgraph/imap.c",
  "lib/cgraph/io.c",
  "lib/cgraph/mem.c",
  "lib/cgraph/node.c",
  "lib/cgraph/obj.c",
  "lib/cgraph/pend.c",
  "lib/cgraph/prisize_t.h",
  "lib/cgraph/rec.c",
  "lib/cgraph/refstr.c",
  "lib/cgraph/sprint.c",
  "lib/cgraph/sprint.h",
  "lib/cgraph/subg.c",
  "lib/cgraph/utils.c",
  "lib/cgraph/write.c",
  "lib/circogen/block.c",
  "lib/circogen/block.h",
  "lib/circogen/blockpath.c",
  "lib/circogen/blockpath.h",
  "lib/circogen/blocktree.c",
  "lib/circogen/blocktree.h",
  "lib/circogen/circo.h",
  "lib/circogen/circpos.c",
  "lib/circogen/circpos.h",
  "lib/circogen/circular.c",
  "lib/circogen/circular.h",
  "lib/circogen/circularinit.c",
  "lib/circogen/deglist.c",
  "lib/circogen/deglist.h",
  "lib/circogen/edgelist.c",
  "lib/circogen/edgelist.h",
  "lib/circogen/nodelist.c",
  "lib/circogen/nodelist.h",
  "lib/common/args.c",
  "lib/common/arith.h",
  "lib/common/arrows.c",
  "lib/common/color.h",
  "lib/common/colorprocs.h",
  "lib/common/colxlate.c",
  "lib/common/const.h",
  "lib/common/ellipse.c",
  "lib/common/emit.c",
  "lib/common/entities.h",
  "lib/common/geom.c",
  "lib/common/geom.h",
  "lib/common/geomprocs.h",
  "lib/common/globals.c",
  "lib/common/globals.h",
  "lib/common/htmllex.c",
  "lib/common/htmllex.h",
  "lib/common/htmltable.c",
  "lib/common/htmltable.h",
  "lib/common/input.c",
  "lib/common/intset.c",
  "lib/common/intset.h",
  "lib/common/labels.c",
  "lib/common/logic.h",
  "lib/common/macros.h",
  "lib/common/memory.c",
  "lib/common/memory.h",
  "lib/common/ns.c",
  "lib/common/output.c",
  "lib/common/pointset.c",
  "lib/common/pointset.h",
  "lib/common/postproc.c",
  "lib/common/ps_font_equiv.h",
  "lib/common/psusershape.c",
  "lib/common/render.h",
  "lib/common/routespl.c",
  "lib/common/shapes.c",
  "lib/common/splines.c",
  "lib/common/taper.c",
  "lib/common/textspan.c",
  "lib/common/textspan.h",
  "lib/common/textspan_lut.c",
  "lib/common/textspan_lut.h",
  "lib/common/timing.c",
  "lib/common/types.h",
  "lib/common/usershape.h",
  "lib/common/utils.c",
  "lib/common/utils.h",
  "lib/common/xml.c",
  "lib/dotgen/acyclic.c",
  "lib/dotgen/aspect.c",
  "lib/dotgen/aspect.h",
  "lib/dotgen/class1.c",
  "lib/dotgen/class2.c",
  "lib/dotgen/cluster.c",
  "lib/dotgen/compound.c",
  "lib/dotgen/conc.c",
  "lib/dotgen/decomp.c",
  "lib/dotgen/dot.h",
  "lib/dotgen/dotinit.c",
  "lib/dotgen/dotprocs.h",
  "lib/dotgen/dotsplines.c",
  "lib/dotgen/fastgr.c",
  "lib/dotgen/flat.c",
  "lib/dotgen/mincross.c",
  "lib/dotgen/position.c",
  "lib/dotgen/rank.c",
  "lib/dotgen/sameport.c",
  "lib/edgepaint/edge_distinct_coloring.c",
  "lib/edgepaint/edge_distinct_coloring.h",
  "lib/edgepaint/furtherest_point.c",
  "lib/edgepaint/furtherest_point.h",
  "lib/edgepaint/intersection.c",
  "lib/edgepaint/intersection.h",
  "lib/edgepaint/lab.c",
  "lib/edgepaint/lab.h",
  "lib/edgepaint/lab_gamut.c",
  "lib/edgepaint/lab_gamut.h",
  "lib/edgepaint/node_distinct_coloring.c",
  "lib/edgepaint/node_distinct_coloring.h",
  "lib/expr/excc.c",
  "lib/expr/excontext.c",
  "lib/expr/exdata.c",
  "lib/expr/exerror.c",
  "lib/expr/exeval.c",
  "lib/expr/exexpr.c",
  "lib/expr/exgram.h",
  "lib/expr/exlib.h",
  "lib/expr/exnospace.c",
  "lib/expr/exopen.c",
  "lib/expr/expr.h",
  "lib/expr/exstash.c",
  "lib/expr/extoken.c",
  "lib/expr/extype.c",
  "lib/expr/exzero.c",
  "lib/fdpgen/clusteredges.c",
  "lib/fdpgen/clusteredges.h",
  "lib/fdpgen/comp.c",
  "lib/fdpgen/comp.h",
  "lib/fdpgen/dbg.c",
  "lib/fdpgen/dbg.h",
  "lib/fdpgen/fdp.h",
  "lib/fdpgen/fdpinit.c",
  "lib/fdpgen/grid.c",
  "lib/fdpgen/grid.h",
  "lib/fdpgen/layout.c",
  "lib/fdpgen/tlayout.c",
  "lib/fdpgen/tlayout.h",
  "lib/fdpgen/xlayout.c",
  "lib/fdpgen/xlayout.h",
  "lib/glcomp/glcompbutton.c",
  "lib/glcomp/glcompbutton.h",
  "lib/glcomp/glcompdefs.h",
  "lib/glcomp/glcompfont.c",
  "lib/glcomp/glcompfont.h",
  "lib/glcomp/glcompimage.c",
  "lib/glcomp/glcompimage.h",
  "lib/glcomp/glcomplabel.c",
  "lib/glcomp/glcomplabel.h",
  "lib/glcomp/glcompmouse.c",
  "lib/glcomp/glcompmouse.h",
  "lib/glcomp/glcomppanel.c",
  "lib/glcomp/glcomppanel.h",
  "lib/glcomp/glcompset.c",
  "lib/glcomp/glcompset.h",
  "lib/glcomp/glcomptextpng.c",
  "lib/glcomp/glcomptextpng.h",
  "lib/glcomp/glcomptexture.c",
  "lib/glcomp/glcomptexture.h",
  "lib/glcomp/glpangofont.c",
  "lib/glcomp/glpangofont.h",
  "lib/glcomp/glutils.c",
  "lib/glcomp/glutils.h",
  "lib/gvc/gvc.c",
  "lib/gvc/gvc.h",
  "lib/gvc/gvcext.h",
  "lib/gvc/gvcint.h",
  "lib/gvc/gvcjob.h",
  "lib/gvc/gvcommon.h",
  "lib/gvc/gvconfig.c",
  "lib/gvc/gvconfig.h",
  "lib/gvc/gvcontext.c",
  "lib/gvc/gvcproc.h",
  "lib/gvc/gvdevice.c",
  "lib/gvc/gvevent.c",
  "lib/gvc/gvio.h",
  "lib/gvc/gvjobs.c",
  "lib/gvc/gvlayout.c",
  "lib/gvc/gvloadimage.c",
  "lib/gvc/gvplugin.c",
  "lib/gvc/gvplugin.h",
  "lib/gvc/gvplugin_device.h",
  "lib/gvc/gvplugin_layout.h",
  "lib/gvc/gvplugin_loadimage.h",
  "lib/gvc/gvplugin_render.h",
  "lib/gvc/gvplugin_textlayout.h",
  "lib/gvc/gvrender.c",
  "lib/gvc/gvtextlayout.c",
  "lib/gvc/gvtool_tred.c",
  "lib/gvc/gvusershape.c",
  "lib/gvpr/actions.c",
  "lib/gvpr/actions.h",
  "lib/gvpr/compile.c",
  "lib/gvpr/compile.h",
  "lib/gvpr/gdefs.h",
  "lib/gvpr/gprstate.c",
  "lib/gvpr/gprstate.h",
  "lib/gvpr/gvpr.c",
  "lib/gvpr/gvpr.h",
  "lib/gvpr/parse.c",
  "lib/gvpr/parse.h",
  "lib/gvpr/queue.c",
  "lib/gvpr/queue.h",
  "lib/gvpr/trie.c",
  "lib/gvpr/trieFA.h",
  "lib/ingraphs/ingraphs.c",
  "lib/ingraphs/ingraphs.h",
  "lib/label/index.c",
  "lib/label/index.h",
  "lib/label/node.c",
  "lib/label/node.h",
  "lib/label/nrtmain.c",
  "lib/label/rectangle.c",
  "lib/label/rectangle.h",
  "lib/label/split.q.c",
  "lib/label/split.q.h",
  "lib/label/xlabels.c",
  "lib/label/xlabels.h",
  "lib/mingle/agglomerative_bundling.cpp",
  "lib/mingle/agglomerative_bundling.h",
  "lib/mingle/edge_bundling.cpp",
  "lib/mingle/edge_bundling.h",
  "lib/mingle/ink.cpp",
  "lib/mingle/ink.h",
  "lib/mingle/nearest_neighbor_graph.cpp",
  "lib/mingle/nearest_neighbor_graph.h",
  "lib/mingle/nearest_neighbor_graph_ann.cpp",
  "lib/neatogen/adjust.c",
  "lib/neatogen/adjust.h",
  "lib/neatogen/bfs.c",
  "lib/neatogen/bfs.h",
  "lib/neatogen/call_tri.c",
  "lib/neatogen/call_tri.h",
  "lib/neatogen/circuit.c",
  "lib/neatogen/closest.c",
  "lib/neatogen/closest.h",
  "lib/neatogen/compute_hierarchy.c",
  "lib/neatogen/conjgrad.c",
  "lib/neatogen/conjgrad.h",
  "lib/neatogen/constrained_majorization.c",
  "lib/neatogen/constrained_majorization_ipsep.c",
  "lib/neatogen/constraint.c",
  "lib/neatogen/defs.h",
  "lib/neatogen/delaunay.c",
  "lib/neatogen/delaunay.h",
  "lib/neatogen/digcola.h",
  "lib/neatogen/dijkstra.c",
  "lib/neatogen/dijkstra.h",
  "lib/neatogen/edges.c",
  "lib/neatogen/edges.h",
  "lib/neatogen/embed_graph.c",
  "lib/neatogen/embed_graph.h",
  "lib/neatogen/fPQ.h",
  "lib/neatogen/geometry.c",
  "lib/neatogen/geometry.h",
  "lib/neatogen/heap.c",
  "lib/neatogen/heap.h",
  "lib/neatogen/hedges.c",
  "lib/neatogen/hedges.h",
  "lib/neatogen/info.c",
  "lib/neatogen/info.h",
  "lib/neatogen/kkutils.c",
  "lib/neatogen/kkutils.h",
  "lib/neatogen/legal.c",
  "lib/neatogen/lu.c",
  "lib/neatogen/matinv.c",
  "lib/neatogen/matrix_ops.c",
  "lib/neatogen/matrix_ops.h",
  "lib/neatogen/mem.h",
  "lib/neatogen/memory.c",
  "lib/neatogen/mosek_quad_solve.c",
  "lib/neatogen/mosek_quad_solve.h",
  "lib/neatogen/multispline.c",
  "lib/neatogen/multispline.h",
  "lib/neatogen/neato.h",
  "lib/neatogen/neatoinit.c",
  "lib/neatogen/neatoprocs.h",
  "lib/neatogen/neatosplines.c",
  "lib/neatogen/opt_arrangement.c",
  "lib/neatogen/overlap.c",
  "lib/neatogen/overlap.h",
  "lib/neatogen/pca.c",
  "lib/neatogen/pca.h",
  "lib/neatogen/poly.c",
  "lib/neatogen/poly.h",
  "lib/neatogen/printvis.c",
  "lib/neatogen/quad_prog_solve.c",
  "lib/neatogen/quad_prog_solver.h",
  "lib/neatogen/quad_prog_vpsc.c",
  "lib/neatogen/quad_prog_vpsc.h",
  "lib/neatogen/randomkit.c",
  "lib/neatogen/randomkit.h",
  "lib/neatogen/sgd.c",
  "lib/neatogen/sgd.h",
  "lib/neatogen/site.c",
  "lib/neatogen/site.h",
  "lib/neatogen/smart_ini_x.c",
  "lib/neatogen/solve.c",
  "lib/neatogen/sparsegraph.h",
  "lib/neatogen/stress.c",
  "lib/neatogen/stress.h",
  "lib/neatogen/stuff.c",
  "lib/neatogen/voronoi.c",
  "lib/neatogen/voronoi.h",
  "lib/ortho/fPQ.c",
  "lib/ortho/fPQ.h",
  "lib/ortho/maze.c",
  "lib/ortho/maze.h",
  "lib/ortho/ortho.c",
  "lib/ortho/ortho.h",
  "lib/ortho/partition.c",
  "lib/ortho/partition.h",
  "lib/ortho/rawgraph.c",
  "lib/ortho/rawgraph.h",
  "lib/ortho/sgraph.c",
  "lib/ortho/sgraph.h",
  "lib/ortho/structures.h",
  "lib/ortho/trap.h",
  "lib/ortho/trapezoid.c",
  "lib/osage/osage.h",
  "lib/osage/osageinit.c",
  "lib/pack/ccomps.c",
  "lib/pack/pack.c",
  "lib/pack/pack.h",
  "lib/patchwork/patchwork.c",
  "lib/patchwork/patchwork.h",
  "lib/patchwork/patchworkinit.c",
  "lib/patchwork/tree_map.c",
  "lib/patchwork/tree_map.h",
  "lib/pathplan/cvt.c",
  "lib/pathplan/inpoly.c",
  "lib/pathplan/pathgeom.h",
  "lib/pathplan/pathplan.h",
  "lib/pathplan/pathutil.h",
  "lib/pathplan/route.c",
  "lib/pathplan/shortest.c",
  "lib/pathplan/shortestpth.c",
  "lib/pathplan/solvers.c",
  "lib/pathplan/solvers.h",
  "lib/pathplan/tri.h",
  "lib/pathplan/triang.c",
  "lib/pathplan/util.c",
  "lib/pathplan/vis.h",
  "lib/pathplan/visibility.c",
  "lib/pathplan/vispath.h",
  "lib/rbtree/misc.c",
  "lib/rbtree/red_black_tree.c",
  "lib/rbtree/red_black_tree.h",
  "lib/rbtree/stack.c",
  "lib/rbtree/stack.h",
  "lib/rbtree/test_red_black_tree.c",
  "lib/sfdpgen/Multilevel.c",
  "lib/sfdpgen/Multilevel.h",
  "lib/sfdpgen/PriorityQueue.c",
  "lib/sfdpgen/PriorityQueue.h",
  "lib/sfdpgen/post_process.c",
  "lib/sfdpgen/post_process.h",
  "lib/sfdpgen/sfdp.h",
  "lib/sfdpgen/sfdpinit.c",
  "lib/sfdpgen/sfdpinternal.h",
  "lib/sfdpgen/sparse_solve.c",
  "lib/sfdpgen/sparse_solve.h",
  "lib/sfdpgen/spring_electrical.c",
  "lib/sfdpgen/spring_electrical.h",
  "lib/sfdpgen/stress_model.c",
  "lib/sfdpgen/stress_model.h",
  "lib/sfdpgen/uniform_stress.c",
  "lib/sfdpgen/uniform_stress.h",
  "lib/sfio/Sfio_f/_sffileno.c",
  "lib/sfio/Sfio_f/_sfgetc.c",
  "lib/sfio/Sfio_f/_sfputc.c",
  "lib/sfio/Sfio_f/_sfslen.c",
  "lib/sfio/sfclose.c",
  "lib/sfio/sfcvt.c",
  "lib/sfio/sfdisc.c",
  "lib/sfio/sfexcept.c",
  "lib/sfio/sfextern.c",
  "lib/sfio/sffilbuf.c",
  "lib/sfio/sfflsbuf.c",
  "lib/sfio/sfhdr.h",
  "lib/sfio/sfio.h",
  "lib/sfio/sfio_t.h",
  "lib/sfio/sfmode.c",
  "lib/sfio/sfnew.c",
  "lib/sfio/sfnputc.c",
  "lib/sfio/sfopen.c",
  "lib/sfio/sfpkrd.c",
  "lib/sfio/sfprintf.c",
  "lib/sfio/sfputr.c",
  "lib/sfio/sfraise.c",
  "lib/sfio/sfrd.c",
  "lib/sfio/sfread.c",
  "lib/sfio/sfresize.c",
  "lib/sfio/sfscanf.c",
  "lib/sfio/sfseek.c",
  "lib/sfio/sfsetbuf.c",
  "lib/sfio/sfsetfd.c",
  "lib/sfio/sfsk.c",
  "lib/sfio/sfstack.c",
  "lib/sfio/sfswap.c",
  "lib/sfio/sfsync.c",
  "lib/sfio/sftable.c",
  "lib/sfio/sftmp.c",
  "lib/sfio/sfungetc.c",
  "lib/sfio/sfvprintf.c",
  "lib/sfio/sfvscanf.c",
  "lib/sfio/sfwr.c",
  "lib/sfio/sfwrite.c",
  "lib/sparse/BinaryHeap.c",
  "lib/sparse/BinaryHeap.h",
  "lib/sparse/DotIO.c",
  "lib/sparse/DotIO.h",
  "lib/sparse/IntStack.c",
  "lib/sparse/IntStack.h",
  "lib/sparse/LinkedList.c",
  "lib/sparse/LinkedList.h",
  "lib/sparse/QuadTree.c",
  "lib/sparse/QuadTree.h",
  "lib/sparse/SparseMatrix.c",
  "lib/sparse/SparseMatrix.h",
  "lib/sparse/clustering.c",
  "lib/sparse/clustering.h",
  "lib/sparse/color_palette.c",
  "lib/sparse/color_palette.h",
  "lib/sparse/colorutil.c",
  "lib/sparse/colorutil.h",
  "lib/sparse/general.c",
  "lib/sparse/general.h",
  "lib/sparse/mq.c",
  "lib/sparse/mq.h",
  "lib/topfish/hierarchy.c",
  "lib/topfish/hierarchy.h",
  "lib/topfish/rescale_layout.c",
  "lib/twopigen/circle.c",
  "lib/twopigen/circle.h",
  "lib/twopigen/twopiinit.c",
  "lib/vmalloc/test.c",
  "lib/vmalloc/vmalloc.c",
  "lib/vmalloc/vmalloc.h",
  "lib/vmalloc/vmclear.c",
  "lib/vmalloc/vmclose.c",
  "lib/vmalloc/vmopen.c",
  "lib/vmalloc/vmstrdup.c",
  "lib/vpsc/block.cpp",
  "lib/vpsc/block.h",
  "lib/vpsc/blocks.cpp",
  "lib/vpsc/blocks.h",
  "lib/vpsc/constraint.cpp",
  "lib/vpsc/constraint.h",
  "lib/vpsc/csolve_VPSC.cpp",
  "lib/vpsc/csolve_VPSC.h",
  "lib/vpsc/generate-constraints.cpp",
  "lib/vpsc/generate-constraints.h",
  "lib/vpsc/pairingheap/PairingHeap.cpp",
  "lib/vpsc/pairingheap/PairingHeap.h",
  "lib/vpsc/pairingheap/dsexceptions.h",
  "lib/vpsc/solve_VPSC.cpp",
  "lib/vpsc/solve_VPSC.h",
  "lib/vpsc/variable.cpp",
  "lib/vpsc/variable.h",
  "lib/xdot/xdot.c",
  "lib/xdot/xdot.h",
  "macosx/GVApplicationDelegate.h",
  "macosx/GVAttributeInspectorController.h",
  "macosx/GVAttributeSchema.h",
  "macosx/GVDocument.h",
  "macosx/GVExportViewController.h",
  "macosx/GVFileNotificationCenter.h",
  "macosx/GVGraphArguments.h",
  "macosx/GVGraphDefaultAttributes.h",
  "macosx/GVWindowController.h",
  "macosx/GVZGraph.h",
  "plugin.demo/xgtk/src/callbacks.c",
  "plugin.demo/xgtk/src/callbacks.h",
  "plugin.demo/xgtk/src/gvdevice_xgtk.c",
  "plugin.demo/xgtk/src/gvplugin_xgtk.c",
  "plugin.demo/xgtk/src/interface.c",
  "plugin.demo/xgtk/src/interface.h",
  "plugin.demo/xgtk/src/support.c",
  "plugin.demo/xgtk/src/support.h",
  "plugin/core/gvloadimage_core.c",
  "plugin/core/gvplugin_core.c",
  "plugin/core/gvrender_core_dot.c",
  "plugin/core/gvrender_core_fig.c",
  "plugin/core/gvrender_core_json.c",
  "plugin/core/gvrender_core_map.c",
  "plugin/core/gvrender_core_mp.c",
  "plugin/core/gvrender_core_pic.c",
  "plugin/core/gvrender_core_pov.c",
  "plugin/core/gvrender_core_ps.c",
  "plugin/core/gvrender_core_svg.c",
  "plugin/core/gvrender_core_tk.c",
  "plugin/core/gvrender_core_vml.c",
  "plugin/devil/gvdevice_devil.c",
  "plugin/devil/gvplugin_devil.c",
  "plugin/dot_layout/gvlayout_dot_layout.c",
  "plugin/dot_layout/gvplugin_dot_layout.c",
  "plugin/gd/gvdevice_gd.c",
  "plugin/gd/gvloadimage_gd.c",
  "plugin/gd/gvplugin_gd.c",
  "plugin/gd/gvrender_gd.c",
  "plugin/gd/gvrender_gd_vrml.c",
  "plugin/gd/gvtextlayout_gd.c",
  "plugin/gdiplus/FileStream.cpp",
  "plugin/gdiplus/FileStream.h",
  "plugin/gdiplus/gvdevice_gdiplus.cpp",
  "plugin/gdiplus/gvloadimage_gdiplus.cpp",
  "plugin/gdiplus/gvplugin_gdiplus.cpp",
  "plugin/gdiplus/gvplugin_gdiplus.h",
  "plugin/gdiplus/gvrender_gdiplus.cpp",
  "plugin/gdiplus/gvtextlayout_gdiplus.cpp",
  "plugin/gdk/gvdevice_gdk.c",
  "plugin/gdk/gvloadimage_gdk.c",
  "plugin/gdk/gvplugin_gdk.c",
  "plugin/glitz/gvdevice_glitz.c",
  "plugin/glitz/gvplugin_glitz.c",
  "plugin/gs/gvloadimage_gs.c",
  "plugin/gs/gvplugin_gs.c",
  "plugin/gtk/callbacks.c",
  "plugin/gtk/callbacks.h",
  "plugin/gtk/gvdevice_gtk.c",
  "plugin/gtk/gvplugin_gtk.c",
  "plugin/gtk/interface.c",
  "plugin/gtk/interface.h",
  "plugin/gtk/support.c",
  "plugin/gtk/support.h",
  "plugin/lasi/gvloadimage_lasi.c",
  "plugin/lasi/gvplugin_lasi.c",
  "plugin/lasi/gvrender_lasi.cpp",
  "plugin/neato_layout/gvlayout_neato_layout.c",
  "plugin/neato_layout/gvplugin_neato_layout.c",
  "plugin/pango/gvgetfontlist.h",
  "plugin/pango/gvgetfontlist_pango.c",
  "plugin/pango/gvloadimage_pango.c",
  "plugin/pango/gvplugin_pango.c",
  "plugin/pango/gvrender_pango.c",
  "plugin/pango/gvtextlayout_pango.c",
  "plugin/poppler/gvloadimage_poppler.c",
  "plugin/poppler/gvplugin_poppler.c",
  "plugin/quartz/GVTextLayout.h",
  "plugin/quartz/gvdevice_quartz.c",
  "plugin/quartz/gvloadimage_quartz.c",
  "plugin/quartz/gvplugin_quartz.c",
  "plugin/quartz/gvplugin_quartz.h",
  "plugin/quartz/gvrender_quartz.c",
  "plugin/quartz/gvtextlayout_quartz.c",
  "plugin/rsvg/gvloadimage_rsvg.c",
  "plugin/rsvg/gvplugin_rsvg.c",
  "plugin/visio/VisioGraphic.cpp",
  "plugin/visio/VisioGraphic.h",
  "plugin/visio/VisioRender.cpp",
  "plugin/visio/VisioRender.h",
  "plugin/visio/VisioText.cpp",
  "plugin/visio/VisioText.h",
  "plugin/visio/gvplugin_visio.c",
  "plugin/visio/gvrender_visio_vdx.cpp",
  "plugin/webp/gvdevice_webp.c",
  "plugin/webp/gvloadimage_webp.c",
  "plugin/webp/gvplugin_webp.c",
  "plugin/xlib/gvdevice_xlib.c",
  "plugin/xlib/gvplugin_xlib.c",
  "rtest/cdiff.c",
  "rtest/check-package-version.c",
  "tclpkg/gdtclft/gdtclft.c",
  "tclpkg/gv/gv.cpp",
  "tclpkg/gv/gv_builtins.c",
  "tclpkg/gv/gv_dummy_init.c",
  "tclpkg/gv/gv_java_init.c",
  "tclpkg/gv/gv_php_init.c",
  "tclpkg/gv/gv_tcl_init.c",
  "tclpkg/tcldot/no_builtins.c",
  "tclpkg/tcldot/tcldot-edgecmd.c",
  "tclpkg/tcldot/tcldot-graphcmd.c",
  "tclpkg/tcldot/tcldot-id.c",
  "tclpkg/tcldot/tcldot-io.c",
  "tclpkg/tcldot/tcldot-nodecmd.c",
  "tclpkg/tcldot/tcldot-util.c",
  "tclpkg/tcldot/tcldot.c",
  "tclpkg/tcldot/tcldot.h",
  "tclpkg/tcldot/tcldot_builtins.c",
  "tclpkg/tclhandle/tclhandle.c",
  "tclpkg/tclhandle/tclhandle.h",
  "tclpkg/tclpathplan/find_ints.c",
  "tclpkg/tclpathplan/intersect.c",
  "tclpkg/tclpathplan/makecw.c",
  "tclpkg/tclpathplan/simple.h",
  "tclpkg/tclpathplan/tclpathplan.c",
  "tclpkg/tclpathplan/wrapper.c",
  "tclpkg/tclstubs/tclInt.h",
  "tclpkg/tclstubs/tclStubLib.c",
  "tclpkg/tkspline/dllEntry.c",
  "tclpkg/tkspline/tkspline.c",
  "tclpkg/tkstubs/tkInt.h",
  "tclpkg/tkstubs/tkStubImg.c",
  "tclpkg/tkstubs/tkStubLib.c",
  "tests/unit_tests/lib/common/command_line.c",
  "windows/cmd/fc-fix/fc-fix.cpp",
  "windows/cmd/lefty/dot2l/dotparse.c",
  "windows/cmd/lefty/dot2l/dotparse.h",
  "windows/gvedit/Application.h",
  "windows/gvedit/GraphX.cpp",
  "windows/gvedit/UAbout.cpp",
  "windows/gvedit/UAbout.h",
  "windows/gvedit/UEditor.cpp",
  "windows/gvedit/UEditor.h",
  "windows/gvedit/UPreProcess.cpp",
  "windows/gvedit/UPreProcess.h",
  "windows/gvedit/UPreview.cpp",
  "windows/gvedit/UPreview.h",
  "windows/gvedit/USettings.cpp",
  "windows/gvedit/USettings.h",
  "windows/gvedit/Umain.cpp",
  "windows/gvedit/Umain.h",
  "windows/include/unistd.h",
)

root = Path(__file__).parents[1]

# ensure developers cannot move/delete a file without being prompted to update
# the above list
for source in EXCLUDE:
  assert (root / source).exists(), \
    f"{source} not found; ci/clang_format.py needs updating?"

# find all C/C++ in the repository
sources = subprocess.check_output(["git", "ls-files", "-z", "--", "**/*.c",
                                   "**/*.h", "**/*.hpp", "**/*.cpp", "**/*.C",
                                   "**/*.c++", "**/*.cxx", "**/*.cc"],
                                  universal_newlines=True)

for source in sources.split("\x00")[:-1]:

  print(f"checking {source}...")

  # FIXME: this file contains invalid UTF-8 characters
  if source == "windows/cmd/fc-fix/fc-fix.cpp":
    print(f"skipping {source} due to malformed content")
    continue

  with open(source, "rt", encoding="utf-8") as f:
    original = f.read()

  # ask `clang-format` to style the file
  reformatted = subprocess.check_output(["clang-format", "--style=file", "--",
                                         source],
                                        cwd=root, universal_newlines=True)

  if source in EXCLUDE:
    # ensure developers cannot make a file compliant without being prompted to
    # remove it from the exclude list
    assert original != reformatted, \
      f"{source} is on the exclude list but is compliant"
    continue

  # were the before and after contents different?
  diff = list(difflib.unified_diff(original.splitlines(keepends=True),
                                   reformatted.splitlines(keepends=True),
                                   fromfile=source, tofile=source))
  if diff:
    print(f"{source} incorrectly formatted:\n{''.join(diff)}", end="")
    sys.exit(-1)