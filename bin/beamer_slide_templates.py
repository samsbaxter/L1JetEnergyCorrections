"""
Templates for various beamer slides, like 4 plots, etc

Robin Aggleton 2015
"""


from itertools import izip
import re

# Needs testing
one_plot_slide = \
r"""
\section{@SLIDE_TITLE}
\begin{frame}{@SLIDE_TITLE}
\vspace{-.3cm}
\begin{center}
@PLOT1TITLE
\\
\scalebox{1.0}{\input{@PLOT1}}
\\
\end{center}
\end{frame}
"""

# Nees testing
two_plot_slide = \
r"""
\section{@SLIDE_TITLE}
\begin{frame}{@SLIDE_TITLE}
\vspace{-.3cm}
\begin{columns}
\begin{column}{0.5\textwidth}
\begin{center}
@PLOT1TITLE
\\
\scalebox{0.5}{\input{@PLOT1}}
\\
\end{center}
\end{column}

\begin{column}{0.5\textwidth}
\begin{center}
@PLOT2TITLE
\\
\scalebox{0.5}{\input{@PLOT2}}
\end{center}
\end{column}
\end{columns}
\end{frame}
"""


four_plot_slide = \
r"""
\section{@SLIDE_TITLE}
\begin{frame}{@SLIDE_TITLE}
\vspace{-.3cm}
\begin{columns}
\begin{column}{0.5\textwidth}
\begin{center}
@PLOT1TITLE
\\
\scalebox{0.55}{\input{@PLOT1}}
\\
@PLOT3TITLE
\\
\scalebox{0.55}{\input{@PLOT3}}
\end{center}
\end{column}

\begin{column}{0.5\textwidth}
\begin{center}
@PLOT2TITLE
\\
\scalebox{0.55}{\input{@PLOT2}}
\\
@PLOT4TITLE
\\
\scalebox{0.55}{\input{@PLOT4}}
\end{center}
\end{column}
\end{columns}
\end{frame}
"""

def make_slide(slide_temp, titles, plotnames, slidetitle=""):
    """
    Auto make a slide, so no faffing around with replace statements.

    slide_temp = template, e.g. four_plot_slide
    title = list of titles for each plot
    plotnames = list of filenames for each plot
    slidetitle = title for this slide
    """

    print "making slide"
    slide = slide_temp.replace("@SLIDE_TITLE", slidetitle)
    for i, item in enumerate(izip(titles, plotnames)):
            slide = slide.replace("@PLOT"+str(i+1)+"TITLE", item[0])
            slide = slide.replace("@PLOT"+str(i+1), item[1])

    # cleanup incase we have leftover unused figures
    slide = re.sub(r"@PLOT\dTITLE", "", slide)
    # r"\\scalebox{0.55}{\input{@PLOT3}}"
    slide = re.sub(r"\\scalebox{0\.\d+}{\\input{@PLOT\d}}", "", slide)  # to avoid "missing .tex file" error
    slide = re.sub(r"\\\\\n\n", "", slide)  # remove useless line breaks
    slide = slide.replace("\n\n\\\\", "\\\\")
    return slide
