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

\RequirePackage{titlesec}
\RequirePackage[UTF8]{ctex}
\RequirePackage[section]{placeins}

\captionsetup{skip=10pt}

\titleformat{\section}{\large\bfseries}{\chinese{section}、}{0em}{}
\titleformat{\subsection}{\normalsize\bfseries}{(\chinese{subsection})}{1em}{}
\titleformat{\subsubsection}{\normalsize\bfseries}{\arabic{subsubsection}.}{1em}{}

\RequirePackage{eso-pic}
\RequirePackage{graphicx}

\newcommand{\@ExamName}{}
\newcommand{\ExamName}[1]{%
  \gdef\@ExamName{#1}%
}

\title{\bfseries \@ExamName}

\date{}
\author{专业：微电子科学与工程 2 班 \quad 姓名：王奕杰 \quad 实验编号：6}

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
    \begin{table}[htbp]
      \centering
      % 先输出“汇总标题”
      \tl_if_blank:nTF {#1}
        {
          \caption*{#2}
        }
        {
          \caption*{表~\ref{#1}：#2}
        }
      % 再输出表体，但不再执行原来的 \caption/\label
      \__exp_record_replay_body:n {#3}
    \end{table}
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
    % \clearpage
    % \section*{实验填写表汇总}
    \seq_map_inline:Nn \g__exp_record_table_seq
      {
        ##1
      }
  }

\ExplSyntaxOff

% \renewcommand{\today}{\small{\the\year 年 \the\month 月 \the\day 日}}
% \renewcommand{\today}{}

\RequirePackage{wallpaper}

\makeatletter
\newcommand{\insertRawDataPage}{
    \newpage\ThisCenterWallPaper{1}{../template/原始数据记录表.pdf}
    \vspace*{1.15cm}
    \hspace{1.8cm}
    \@ExamName
    \vspace*{1cm}
    \PrintAllLabRecordTables
}
\makeatother

\newcommand{\insertSignedDataPage}{
	\clearpage
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
