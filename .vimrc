set nocompatible
filetype off

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

Plugin 'VundleVim/Vundle.vim'

Plugin 'vim-scripts/indentpython.vim'
let g:SimpylFold_docstring_preview=1 " see the docstrings for folded code

Plugin 'nvie/vim-flake8' "pep8 check
"Plugin 'scrooloose/syntastic' "syntax check
"
Plugin 'w0rp/ale' "syntax chech in the fly
let g:ale_sign_column_always = 1
" let g:ale_lint_on_text_changed='normal'
let g:ale_python_flake8_args = '--ignore=E,W,F403,F405 --select=F,C'


Plugin 'scrooloose/nerdtree' "file tree
Plugin 'kien/ctrlp.vim' "search for basically anything from VIM
Plugin 'Lokaltog/powerline', {'rtp': 'powerline/bindings/vim/'}
Plugin 'tpope/vim-fugitive'
Plugin 'tmhedberg/SimpylFold'
Plugin 'vim-scripts/simple-pairs'

Plugin 'thinca/vim-quickrun'
let g:quickrun_config = {
      \'*': {
      \'outputter/buffer/split': ':rightbelow vsplit'},}
nnoremap <silent> <F5> :QuickRun<CR>
" inoremap <silent> <Esc><F5> :QuickRun<CR>

Bundle 'Valloric/YouCompleteMe'
let g:ycm_python_binary_path = '/usr/bin/python3'
Plugin 'The-NERD-Commenter'
" Add spaces after comment delimiters by default
let g:NERDSpaceDelims = 1
" Allow commenting and inverting empty lines (useful when commenting a region)
let g:NERDCommentEmptyLines = 1
" Align line-wise comment delimiters flush left instead of following code indentation
let g:NERDDefaultAlign = 'left'
" nnoremap <C-D> :call NERDComment(0,"toggle")<CR>
noremap <silent> <C-D> :call NERDComment(0,"toggle")<CR>
" vnoremap <C-D> :call NERDComment(0,"toggle")<CR>
" inoremap <C-D> :call NERDComment(0,"toggle")<CR>

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
""""""" end for Vundle
let g:ycm_autoclose_preview_window_after_completion=1
map <leader>g  :YcmCompleter GoToDefinition<CR>
map <leader>d  :YcmCompleter GetDoc<CR>
"let python_highlight_all=1
syntax on
let NERDTreeIgnore=['\.pyc$', '\~$'] "ignore files in NERDTree

"split navigations
nnoremap <C-J> <C-W><C-J>
nnoremap <C-K> <C-W><C-K>
nnoremap <C-L> <C-W><C-L>
nnoremap <C-H> <C-W><C-H>

" Enable folding
set foldmethod=indent
set foldlevel=99
" Enable folding with the spacebar
nnoremap <space> za

" Python
au BufNewFile,BufRead *.py;
    \ set tabstop=4
    \ set softtabstop=4
    \ set shiftwidth=4
    \ set textwidth=79
    \ set expandtab
    \ set autoindent
    \ set fileformat=unix
"au BufRead,BufNewFile *.py,*.pyw,*.c,*.h ; match BadWhitespace /\s\+$/
set encoding=utf-8

"filetype plugin on
" allow backspacing over everything in insert mode
set backspace=indent,eol,start
set nobackup		" DON'T keep a backup file

" nnoremap <buffer> <F5> :exec w !python <CR>
" autocmd FileType python nnoremap <buffer> <F5> :w<cr>:!python > temp<CR>
autocmd FileType c set omnifunc=ccomplete#Complete

"set showtabline=2               " File tabs allways visible
":nmap <C-S-tab> :tabprevious<cr>
":nmap <C-tab> :tabnext<cr>
":nmap <C-t> :tabnew<cr>
":map <C-t> :tabnew<cr>
":map <C-S-tab> :tabprevious<cr>
":map <C-tab> :tabnext<cr>
":map <C-w> :tabclose<cr>
":imap <C-S-tab> <ESC>:tabprevious<cr>i
":imap <C-tab> <ESC>:tabnext<cr>i
":imap <C-t> <ESC>:tabnew<cr>

set history=50		" keep 50 lines of command line history
set ruler			" show the cursor position all the time
set showcmd			" display incomplete commands
set incsearch		" do incremental searching
set bg=dark
set hls
set rdt=3000
set tabstop=4

set number relativenumber				" line numbers relative
set cindent								" guess what indent should be used (c-like)
set autoindent							" cp indent from previous line
set mouse=r								" use mouse in xterm to scroll
set scrolloff=10 						" 5 lines bevore and after the current line when scrolling
set ignorecase							" ignore case
set smartcase							" but don't ignore it, when search string contains uppercase letters
set hid 								" allow switching buffers, which have unsaved changes
set shiftwidth=4						" 4 characters for indenting
set showmatch							" showmatch: Show the matching bracket for the last ')'?

set splitbelow 							" open new split below current
set splitright							" open new split to the right

set formatoptions=1
set lbr
syn on
set completeopt=menu,longest,preview
set confirm

" set statusline=%<%f%h%m%r%=%b\ 0x%B\ \ %l,%c%V\ %P	"wyswietlanie numeru znaku w menu
set laststatus=2
" imap jj			<Esc>

" mapowanie nowych klawiszy map, do odmapowanie inne; map jest dla wszystkich, cmap dla command line, nmap normal mode itd

cmap	Q	quit

au BufRead /tmp/mutt-* set tw=60
au BufRead /tmp/mutt-* set formatoptions=1aw
au BufRead /tmp/mutt-* set noautoindent
au BufRead /tmp/mutt-* set nocindent

colorscheme gruvbox

" webcode
au BufNewFile,BufRead *.js, *.html, *.css
    \ set tabstop=2
    \ set softtabstop=2
    \ set shiftwidth=2

set wildignorecase
set timeoutlen=1000 
set ttimeoutlen=10
