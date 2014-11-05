#
# svn-churn.py - determine file churn and fix count for Subversion repository.
#
# Example: python svn-churn.py |sort -n -t , +2 | tail -n 50 |sort -r -n -t , +2
#
# Runs with Python 2.7, 3.3
#
# License: MIT, see accompanying LICENSE.txt
#

# ------------------------------------------------------------------------
# Configuration:

# Repository: working copy path, or URL
# cfg_reposes = ['https://svn.webkit.org/repository/webkit/trunk']
cfg_reposes = []

# Recognise as fix:
cfg_fixed_issues = (
    '[Ii]ssue[s]? #',
    '[Ff]ix',
    '[Cc]orrect'
)

# Substitute partial path with replacement
cfg_edited_paths = (
#    ( r'/trunk/Source/core/', '/trunk/Source/WebCore/' ),
#    ( r'/trunk/Source/'     , ''                       ),
 )

# Subversion command:
cfg_svn = 'svn'

# ------------------------------------------------------------------------

import re, subprocess, sys

class Context:
    def __init__( self, svn, fixed_issues, edited_paths ):
        self.svn = svn
        self.fixed_issues = fixed_issues
        self.edited_paths = edited_paths

class Churn:
    """storage: { path : [ changed, fixed, [messages] ] }
    """
    def __init__( self, context ):
        self.context  = context
        self.storage  = dict()
        self.edits    = self.create_edits( context.edited_paths )

    def __call__( self, reposes, options ):
        for repos in reposes:
            self.parse_svn_log( self.svn_log( repos, options ) )
        self.update_fixes()
        self.print_results( reposes )

    def svn_log( self, repos, options ):
        command = [ self.context.svn, 'log', '-v' ] + options + [ repos ]
        process = subprocess.Popen( command, stdout=subprocess.PIPE, universal_newlines=True )
        out, err = process.communicate()
        return out

    def issue_pattern( self ):
        result = ''
        for p in self.context.fixed_issues:
            result += p if 0==len(result) else '|' + p
        return r'(' + result + ')'

    def update_fixes( self ):
        for k, v in self.storage.items():
            pattern = re.compile( self.issue_pattern() )
            for m in v[2]:
                if pattern.search( m ):
                    v[1] += 1

    def print_results( self, reposes ):
        print( 'Churn,Fixes,Churn*Fixes,File {reposes}'.format( reposes=reposes) )
        for k, v in self.storage.items():
            print( "{chg},{fix},{prod},{path}".format( chg=v[0], fix=v[1], prod=v[0] * v[1], path=k ) )

    def parse_svn_log( self, text ):
        s_dash     = 1
        s_revision = 2
        s_paths    = 3
        s_message  = 4

        state = s_dash

        for line in text.split( '\n' ):
            if state == s_dash:
                state = s_revision
            elif state == s_revision:
                msg = ''
                files = []
                state = s_paths
            elif state == s_paths:
                if line.startswith( 'Changed paths:' ):
                    continue
                elif line == '':
                    state = s_message
                else:
                    files.append( line )
            elif state == s_message:
                if line.startswith( '-----' ):
                    for name in files:
                        self.store( name, msg )
                    state = s_revision
                else:
                    if msg == '':
                        msg = line
                    else:
                        msg += '|' + line

    def store( self, name, msg ):
        name = self.edit_path( name )
        if name in self.storage:
            self.storage[ name ][0] += 1
            self.storage[ name ][2].append( msg )
        else:
            self.storage[ name ] = [ 1, 0, [msg] ]

    def edit_path( self, path ):
        for (p,r) in self.edits:
            path = p.sub( r, path )
        return path

    def create_edits( self, edited_paths ):
        result = [ ( re.compile( r'\s+[ADMR] /' ), '/' ) ]
        for (p,r) in edited_paths:
            result.append( ( re.compile( p ), r ) )
        return result

def usage():
    print(
"""Usage: svn-churn [options] [repos...]

Options
    -h, --help  this help screen
            --  end options section
    Other options upto -- are passed on to the 'svn log' command.

svn-churn mines the log of the given Subversion repository
and presents the number of changes and fixes for each file.
Repos can be specified as a working copy path or a URL.

Examples
    Use repositories configured in script:
        ./svn-churn.py

    Use repositories configured in script and limit log used to latest 200 items:
        ./svn-churn.py --limit 200 --

    Report 50 most changed and fixed files (sort on changes*fixes):
        ./svn-churn.py |sort -n -t , +2 | tail -n 50 |sort -r -n -t , +2

Note
    Among a few other things, you can configure the SVN repository in the script.""" )

def split_arguments( arguments ):
    options = []
    inputs  = []
    opt_help = False
    in_options = True

    for arg in arguments:
        if in_options:
            if   arg == '--'                   : in_options = False; continue
            elif arg == '-h' or '--help' == arg: opt_help   = True ; continue
            else: options.append( arg ); continue
        inputs.append( arg )
    return ( opt_help, options, cfg_reposes if len(inputs) == 0 else inputs )

def help( opt_help, reposes ):
    return opt_help or len( reposes ) == 0

def main( arguments ):
    churn = Churn( Context( cfg_svn, cfg_fixed_issues, cfg_edited_paths ) )

    ( opt_help, svn_options, svn_reposes ) = split_arguments( arguments[1:] )

    if help( opt_help, svn_reposes ):
        return usage()

    churn( svn_reposes, svn_options )

if __name__ == "__main__":
    try:
        main( sys.argv )
    except Exception as e:
        output = e # transform representation to message
        print( "Error: {e}".format( e=output ) )

#
# end of file
#
