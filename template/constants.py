# STATUS constants returned by directives
STATUS_OK = 0      # ok
STATUS_RETURN = 1      # ok, block ended by RETURN
STATUS_STOP = 2      # ok, stoppped by STOP
STATUS_DONE = 3      # ok, iterator done
STATUS_DECLINED = 4      # ok, declined to service request
STATUS_ERROR = 255      # error condition

# ERROR constants for indicating exception types
ERROR_RETURN = 'return' # return a status code
ERROR_FILE = 'file'   # file error: I/O, parse, recursion
ERROR_VIEW = 'view'   # view error
ERROR_UNDEF = 'undef'  # undefined variable value used
ERROR_PERL = 'perl'   # error in [% PERL %] block
ERROR_FILTER = 'filter' # filter error
ERROR_PLUGIN = 'plugin' # plugin error

# CHOMP constants for PRE_CHOMP and POST_CHOMP
CHOMP_NONE = 0 # do not remove whitespace
CHOMP_ALL = 1 # remove whitespace up to newline
CHOMP_ONE = 1 # new name for CHOMP_ALL
CHOMP_COLLAPSE = 2 # collapse whitespace to a single space
CHOMP_GREEDY = 3 # remove all whitespace including newlines

# DEBUG constants to enable various debugging options
DEBUG_OFF = 0 # do nothing
DEBUG_ON = 1 # basic debugging flag
DEBUG_UNDEF = 2 # throw undef on undefined variables
DEBUG_VARS = 4 # general variable debugging
DEBUG_DIRS = 8 # directive debugging
DEBUG_STASH = 16 # general stash debugging
DEBUG_CONTEXT = 32 # context debugging
DEBUG_PARSER = 64 # parser debugging
DEBUG_PROVIDER = 128 # provider debugging
DEBUG_PLUGINS = 256 # plugins debugging
DEBUG_FILTERS = 512 # filters debugging
DEBUG_SERVICE = 1024 # context debugging
DEBUG_ALL = 2047 # everything

# extra debugging flags
DEBUG_CALLER = 4096 # add caller file/line
DEBUG_FLAGS = 4096 # bitmask to extraxt flags

## $DEBUG_OPTIONS  = {
##     &DEBUG_OFF      => off      => off      => &DEBUG_OFF,
##     &DEBUG_ON       => on       => on       => &DEBUG_ON,
##     &DEBUG_UNDEF    => undef    => undef    => &DEBUG_UNDEF,
##     &DEBUG_VARS     => vars     => vars     => &DEBUG_VARS,
##     &DEBUG_DIRS     => dirs     => dirs     => &DEBUG_DIRS,
##     &DEBUG_STASH    => stash    => stash    => &DEBUG_STASH,
##     &DEBUG_CONTEXT  => context  => context  => &DEBUG_CONTEXT,
##     &DEBUG_PARSER   => parser   => parser   => &DEBUG_PARSER,
##     &DEBUG_PROVIDER => provider => provider => &DEBUG_PROVIDER,
##     &DEBUG_PLUGINS  => plugins  => plugins  => &DEBUG_PLUGINS,
##     &DEBUG_FILTERS  => filters  => filters  => &DEBUG_FILTERS,
##     &DEBUG_SERVICE  => service  => service  => &DEBUG_SERVICE,
##     &DEBUG_ALL      => all      => all      => &DEBUG_ALL,
##     &DEBUG_CALLER   => caller   => caller   => &DEBUG_CALLER,
## };

## @STATUS  = qw( STATUS_OK STATUS_RETURN STATUS_STOP STATUS_DONE
##                STATUS_DECLINED STATUS_ERROR );
## @ERROR   = qw( ERROR_FILE ERROR_VIEW ERROR_UNDEF ERROR_PERL 
##                ERROR_RETURN ERROR_FILTER ERROR_PLUGIN );
## @CHOMP   = qw( CHOMP_NONE CHOMP_ALL CHOMP_ONE CHOMP_COLLAPSE CHOMP_GREEDY );
## @DEBUG   = qw( DEBUG_OFF DEBUG_ON DEBUG_UNDEF DEBUG_VARS 
##                DEBUG_DIRS DEBUG_STASH DEBUG_CONTEXT DEBUG_PARSER
##                DEBUG_PROVIDER DEBUG_PLUGINS DEBUG_FILTERS DEBUG_SERVICE
##                DEBUG_ALL DEBUG_CALLER DEBUG_FLAGS );

## sub debug_flags {
##     my ($self, $debug) = @_;
##     my (@flags, $flag, $value);
##     $debug = $self unless defined($debug) || ref($self);
##     
##     if ($debug =~ /^\d+$/) {
##         foreach $flag (@DEBUG) {
##             next if $flag =~ /^DEBUG_(OFF|ALL|FLAGS)$/;
## 
##             # don't trash the original
##             my $copy = $flag;
##             $flag =~ s/^DEBUG_//;
##             $flag = lc $flag;
##             return $self->error("no value for flag: $flag")
##                 unless defined($value = $DEBUG_OPTIONS->{ $flag });
##             $flag = $value;
## 
##             if ($debug & $flag) {
##                 $value = $DEBUG_OPTIONS->{ $flag };
##                 return $self->error("no value for flag: $flag") unless defined $value;
##                 push(@flags, $value);
##             }
##         }
##         return wantarray ? @flags : join(', ', @flags);
##     }
##     else {
##         @flags = split(/\W+/, $debug);
##         $debug = 0;
##         foreach $flag (@flags) {
##             $value = $DEBUG_OPTIONS->{ $flag };
##             return $self->error("unknown debug flag: $flag") unless defined $value;
##             $debug |= $value;
##         }
##         return $debug;
##     }
## }
