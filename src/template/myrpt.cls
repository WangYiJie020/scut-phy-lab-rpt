\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{myrpt}[My Template]

\LoadClass{article} % 继承自 article 类

\RequirePackage{xeCJK}
% \RequirePackage[a4paper,top=2.54cm,bottom=2.54cm,left=3.18cm,right=3.18cm]{geometry} % ,marginparwidth=1.75cm
\RequirePackage[a4paper,top=2cm,bottom=2cm,left=3cm,right=3cm]{geometry} % ,marginparwidth=1.75cm
\RequirePackage{graphicx}
\RequirePackage{siunitx}
\RequirePackage{amsmath,amssymb,amsthm}
\RequirePackage{booktabs}
\RequirePackage{tikz}
\RequirePackage{enumitem}
\RequirePackage{pgfplots}
\RequirePackage[colorlinks=true, allcolors=blue]{hyperref}

\RequirePackage{enumitem}
\RequirePackage{booktabs} % 三线表
\RequirePackage{tabularx}
\RequirePackage{caption}
\RequirePackage{pdfpages}

\RequirePackage{titling}
\RequirePackage{fancyhdr}

\RequirePackage[UTF8,fontset=none,heading=true]{ctex}
\RequirePackage[section]{placeins}

\captionsetup{skip=10pt}

% 正文宋体，加粗与标题用黑体（对齐数模模板习惯）
\setCJKmainfont{SimSun}[
  AutoFakeSlant = true,
  BoldFont = SimHei
]
\setCJKsansfont{SimHei}[
  AutoFakeSlant = true
]
\setCJKmonofont{SimSun}
\newCJKfontfamily[hei]\heiti{SimHei}
\newCJKfontfamily[song]\songti{SimSun}

\ctexset{
  section = {
    format = \centering\zihao{4}\heiti,
    nameformat = {},
    titleformat = {},
    aftername = \hspace{0.6em},
    beforeskip = 1.2ex plus .2ex,
    afterskip = 1.0ex plus .2ex
  },
  subsection = {
    format = \raggedright\zihao{-4}\heiti,
    aftername = \hspace{0.5em},
    beforeskip = 1.0ex plus .2ex,
    afterskip = 0.7ex plus .2ex
  },
  subsubsection = {
    format = \raggedright\zihao{-4}\heiti,
    aftername = \hspace{0.5em},
    beforeskip = 0.8ex plus .2ex,
    afterskip = 0.5ex plus .2ex
  }
}

\RequirePackage{eso-pic}
\RequirePackage{graphicx}

\newcommand{\@ExamName}{}
\newcommand{\ExamName}[1]{%
  \gdef\@ExamName{#1}%
}

\title{\heiti \@ExamName}

\setlength{\headheight}{14pt}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small 大学物理实验报告}
\fancyhead[R]{\small \@ExamName}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}

\newcommand{\StuName}{王奕杰}
\newcommand{\StuID}{20564830965}
\newcommand{\StuClass}{微电子科学与工程 2 班}
\newcommand{\ClassPeriod}{2026-2027 学年第一学期}

\date{}
\author{专业：\StuClass \quad 姓名：\StuName \quad 实验编号：9}

\newtheorem{problem}{题}
\newenvironment{solution}
{\begin{proof}[\textbf{解}]\renewcommand{\qedsymbol}{}}
{\end{proof}}

% 自动汇总数据表格

\RequirePackage{expl3,xparse}
\RequirePackage{longtable}

\ExplSyntaxOn

% 全局序列：保存所有需要汇总重复输出的表
\seq_new:N \g__exp_record_table_seq

% 临时变量：记录当前表的 caption / label
\tl_new:N \l__exp_record_caption_tl
\tl_new:N \l__exp_record_label_tl

% 备份原始 \caption / \label
\cs_new_eq:NN \__exp_record_orig_caption \caption
\cs_new_eq:NN \__exp_record_orig_label   \label

% 用于重印时执行表体，但屏蔽里面原有的 \caption 和 \label
\cs_new_protected:Nn \__exp_record_replay_body:n
  {
    \group_begin:
      \RenewDocumentCommand \caption { s o m } {}
      \RenewDocumentCommand \label   { m } {}
      #1
    \group_end:
  }

% 汇总输出单条记录
\cs_new_protected:Nn \__exp_record_print_saved:nnn
  {
    \par
    \noindent
    \begin{minipage}{\linewidth}
      \centering
      \captionsetup{type=table}
      \tl_if_blank:nTF {#1}
        {
          \captionof*{table}{#2}
        }
        {
          \captionof*{table}{表~\ref{#1}：#2}
        }
      \__exp_record_replay_body:n {#3}
    \end{minipage}
    \par
    \vspace{0.5\baselineskip}
  }

% 主环境：正文里正常写 \caption 和 \label
\NewDocumentEnvironment{LabRecordTable}{ O{htbp} +b }
  {
    \group_begin:
      \tl_gclear:N \l__exp_record_caption_tl
      \tl_gclear:N \l__exp_record_label_tl

      \RenewDocumentCommand \caption { s o m }
        {
          \tl_gset:Nn \l__exp_record_caption_tl {##3}
          \IfBooleanTF{##1}
            {
              \IfNoValueTF{##2}
                { \__exp_record_orig_caption*{##3} }
                { \__exp_record_orig_caption*[##2]{##3} }
            }
            {
              \IfNoValueTF{##2}
                { \__exp_record_orig_caption{##3} }
                { \__exp_record_orig_caption[##2]{##3} }
            }
        }

      \RenewDocumentCommand \label { m }
        {
          \tl_gset:Nn \l__exp_record_label_tl {##1}
          \__exp_record_orig_label{##1}
        }

      \begin{table}[#1]
        #2
      \end{table}

      \seq_gput_right:Nx \g__exp_record_table_seq
        {
          \__exp_record_print_saved:nnn
            { \exp_not:V \l__exp_record_label_tl }
            { \exp_not:V \l__exp_record_caption_tl }
            { \exp_not:n {#2} }
        }
    \group_end:
  }
  {}

% 文末统一打印
\NewDocumentCommand{\PrintAllLabRecordTables}{}
  {
    \group_begin:
      \setlength{\abovecaptionskip}{2pt}
      \setlength{\belowcaptionskip}{4pt}
      \setlength{\parskip}{0pt}
      \seq_map_inline:Nn \g__exp_record_table_seq
        {
          ##1
        }
    \group_end:
  }

\ExplSyntaxOff

% \renewcommand{\today}{\small{\the\year 年 \the\month 月 \the\day 日}}
% \renewcommand{\today}{}

\RequirePackage{wallpaper}

\makeatletter
\newcommand{\insertRawDataPage}{
	\newpage\ThisCenterWallPaper{1}{../template/原始数据记录表.pdf}
	\thispagestyle{empty}
	\vspace*{1.05cm}
	\hspace{1.8cm}
	\@ExamName
	\vspace*{1cm}
	\PrintAllLabRecordTables
}
\makeatother


\makeatletter
\newcommand{\insertCoverPage}{

	\newgeometry{margin=0pt} % 使得位置从无页边距开始

	\newpage\ThisCenterWallPaper{1}{../template/封面.pdf}
	\thispagestyle{empty}

	% \vspace in horizontal mode is deferred, so overlay the form fields
	% with absolute page coordinates instead of stacking hspace/vspace.
	\AddToShipoutPictureFG*{
		\AtPageLowerLeft{
			\begin{tikzpicture}[overlay, inner sep=0pt]
				\node[anchor=west, font=\large] at (10.80cm, {\paperheight-13.017cm}) {\@ExamName};
				\node[anchor=west, font=\large] at (10.80cm, {\paperheight-14.167cm}) {\StuName};
				\node[anchor=west, font=\large] at (10.80cm, {\paperheight-15.316cm}) {\StuID};
				\node[anchor=west, font=\large] at (10.80cm, {\paperheight-16.459cm}) {\StuClass};
				\node[anchor=west, font=\large] at (10.80cm, {\paperheight-17.602cm}) {\ClassPeriod};
			\end{tikzpicture}
		}
	}
	\null

	\newpage
	\restoregeometry
	\makeIntentionallyBlankPage
	\setcounter{page}{1}
}
\makeatother

\newcommand{\makeIntentionallyBlankPage}{%
	\thispagestyle{empty}%
	\AddToShipoutPictureFG*{%
		\AtPageLowerLeft{%
			\begin{tikzpicture}[overlay, inner sep=0pt]
				\node[
					font=\LARGE\sffamily,
					text=black,
					opacity=0.18,
					align=center
				] at (0.5\paperwidth, 0.5\paperheight)
					{This page is intentionally left blank.};
			\end{tikzpicture}%
		}%
	}%
	\null
	\clearpage
}

\newcommand{\insertSignedDataPage}{
	\clearpage
	\ifodd\value{page}
	\else
		\makeIntentionallyBlankPage
	\fi
	\thispagestyle{empty}
	\AddToShipoutPicture*{
		\put(0,0){
			\parbox[b][\paperheight]{\paperwidth}{
				\vfill
				\centering
				\includegraphics[width=\paperwidth,height=\paperheight]{data/signed_RawRecord.jpg}
				\vfill
			}
		}
	}
	% \noindent 附件：原始数据
	\section*{附件：原始数据}
}


\date{}
