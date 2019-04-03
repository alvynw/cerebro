import random
import time
import sys

def run_arithmetic(args, options, param=-1, merge_opens=True, \
                   reallocate=True, debug=False):
    
    from Compiler.program import Program
    from Compiler.config import *
    from Compiler.exceptions import *
    import instructions, instructions_base, types, comparison, library

    import interface
    from interface import ASTParser as ASTParser
    import inspect

    interface.mpc_type = interface.SPDZ

    _interface = [t[1] for t in inspect.getmembers(interface, inspect.isclass)]
    for op in _interface:
        VARS[op.__name__] = op    
    
    """ Compile a file and output a Program object.
    
    If merge_opens is set to True, will attempt to merge any parallelisable open
    instructions. """
    
    prog = Program(args, options, param)
    instructions.program = prog
    instructions_base.program = prog
    types.program = prog
    comparison.program = prog
    prog.DEBUG = debug
    
    VARS['program'] = prog
    comparison.set_variant(options)
    
    print 'Compiling file', prog.infile
    
    if instructions_base.Instruction.count != 0:
        print 'instructions count', instructions_base.Instruction.count
        instructions_base.Instruction.count = 0
    prog.FIRST_PASS = False
    prog.reset_values()
    # make compiler modules directly accessible
    sys.path.insert(0, 'Compiler')
    # create the tapes
    print 'Compiling file', prog.infile
    a = ASTParser(prog.infile, debug=True)
    a.parse()
    a.execute(VARS)    

    # optimize the tapes
    for tape in prog.tapes:
        tape.optimize(options)
    
    if prog.main_thread_running:
        prog.update_req(prog.curr_tape)
    print 'Program requires:', repr(prog.req_num)
    print 'Memory size:', prog.allocated_mem

    # finalize the memory
    prog.finalize_memory()

    return prog


# Similar 
def run_gc(args, options, param=-1, merge_opens=True, \
           reallocate=True, debug=False):

    from Compiler.program_gc import ProgramGC
    import instructions_gc, types_gc
    import interface
    from interface import ASTParser as ASTParser
    import inspect

    interface.mpc_type = interface.GC

    _interface = [t[1] for t in inspect.getmembers(interface, inspect.isclass)]
    for op in _interface:
        VARS[op.__name__] = op
    
    prog = ProgramGC(args, options, param)
    instructions_gc.program_gc = prog
    types_gc.program_gc = prog
    VARS['program_gc'] = prog

    print 'Compiling file', prog.infile
    a = ASTParser(prog.infile, debug=True)
    a.parse()
    a.execute(VARS)

    return prog


def run(args, options, param=-1, merge_opens=True, \
        reallocate=True, debug=False):

    if args[1] == 'a':
        return run_arithmetic(args, options, param, merge_opens=merge_opens, debug=debug)
    elif args[1] == 'b':
        return run_gc(args, options, param, merge_opens=merge_opens, debug=debug)
    else:
        raise ValueError("Must choose either arithmetic (a) or GC (b)")
