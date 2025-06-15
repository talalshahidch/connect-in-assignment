"""
External API to interace with student code

It is not possible to make students completely unaware of the code in this folder. We 
do have to provide some hooks for them to use to integrate their code. These hooks are
set_choice and get_choice listed below. These functions are both designed to run 
asynchronously; student code and our interface code run in separate threads. This is
necessary to support graphical input and animation.

Author: Walker M. White (wmw2)
Date:   September 28, 2023
"""
import threading
import traceback
import ctypes


class SharedBuffer(object):
    """
    This class represents a shared buffer implementing producer-consumer behavior.
    
    The buffer is by-directional, meaning that either thread can be the producer or
    the consumer. But only one of the two threads will block on this (student code)
    while the other is always running (e.g. animation).  We typically think of the
    blocking thread as the consumer, because the other thread (via busy waiting) will
    produce a value in response.
    
    This class is implemented as a singleton to allow students to access it without
    having to instantiate it first. 
    """
    # HIDDEN INSTANCE ATTRIBUTES
    # Attribute _data: The shared buffer
    # Invariant: _data is a list (of anything)
    #
    # Attribute _blocked: Whether a "consumer" is currently blocked on this buffer
    # Invariant: _blocked is bool
    #
    # Attribute _invalid: Whether the shared buffer is invalid (deactivated)
    # Invariant: _invalid is a bool
    
    # CLASS ATTRIBUTE: Condition variable for synchronization
    # This is a class variable as it must exist BEFORE the singleton is instantiated
    # Otherwise, we get race conditions on __new__.
    cond = threading.Condition()
    
    def __new__(cls):
        """
        Returns the singleton instance of this class.
        
        This method only instantiates the class once, storing the result in a class
        attribute.  Future allocations will access this cached object
        """
        with cls.cond:  # Prevent race on allocation
            if not hasattr(cls, 'instance'):
                cls.instance = super(SharedBuffer, cls).__new__(cls)
                cls.instance._private_init_()
            return cls.instance
    
    def _private_init_(self):
        """
        Initializes the shared buffer
        
        This is a private initializer, as the public initializer will be called every
        time the singleton is 'allocated' (e.g. it can be called multiple times).
        """
        self.data = []
        self.blocked = False
        self.invalid = False
    
    def isBlocked(self):
        """
        Returns true if a thread is blocked on this shared buffer.
        
        This class is designed to have one thread that blocks on a condition, while 
        another uses busy waiting to mainting real-time animation.  This method is used
        by the busy-waiting thread to check for a waiting consumer.
        """
        value = False
        with self.cond:
            value = self.blocked
        return value

    def isInvalid(self):
        """
        Returns true if this buffer is invalid.
        
        An invalid buffer can no longer be used.  Any blocked threads will immediately
        experience a Runtime Error, and all other methods will fail. This is used to
        clean-up any held locks.
        """
        value = False
        with self.cond:
            value = self.invalid
        return value
    
    def block(self):
        """
        Blocks the current thread on this shared buffer.
        
        This method blocks until another thread calls unblock() or invalidates the 
        shared buffer. If the buffer is invalidated while a thread is blocked on this
        method, this method raises a RuntimeError.
        """
        with self.cond:
            self.blocked = True
            while self.blocked:
                if self.invalid:
                    raise RuntimeError()
                self.cond.wait()
    
    def unblock(self):
        """
        Unblocks the next thread waiting on this shared buffer.
        
        If block() has been called multiple times, only one thread is unblocked. This 
        function does nothing if the buffer is invalid.
        """
        with self.cond:
            if not self.invalid:
                self.blocked = False
                self.cond.notify()
    
    def post(self,value):
        """
        Posts a value to the shared buffer
        
        The value is added to the end of the buffer (e.g. the buffer is a queue).
        
        If this buffer is invalid, this function will do nothing.
        
        Parameter value: The value to post
        Precondition: NONE
        """
        with self.cond:
            if not self.invalid:
                self.data.append(value)
    
    def poll(self):
        """
        Pulls a value from the shared buffer
        
        The value is removed from the front of the buffer (e.g. the buffer is a queue).
        The value can be of any type.
        
        If this buffer is invalid, this function will return None.
        """
        value = None
        try:
            with self.cond:
                if not self.invalid:
                    value = self.data.pop(0)
        except:
            pass
        return value
    
    def invalidate(self):
        """
        Invalidates this buffer.
        
        All blocking threads are immediately notified and sent a RuntimeError. After 
        this method is called, no mutable method will function until reset() is called.
        """
        with self.cond:
            self.invalid = True
            self.cond.notify_all()
    
    def reset(self):
        """
        Resets an invalidate buffer.
        
        All attributes are restored to their intial values and all blocking threads
        are notified.
        
        This method does nothing if the buffer is still valid.
        """
        with self.cond:
            if self.invalid:
                self.data = []
                self.blocked = False
                self.invalid = False
                self.cond.notify_all()


class SafeThread(object):
    """
    A class implementing a thread that can be safely killed.
    
    Threads in Python cannot be killed. You can wait on them to die, but if they are
    holding any locks, that can be a long time.  This version of thread allows us
    to kill a thread in such a way that all locks are released.  While this could 
    result in inconsistent program state, this typically reserved for clean-up just
    before a program exits.
    
    This class mostly implements the public facing API of Thread and can be used the
    same way.
    """

    @property
    def name(self):
        """
        A string used for identification purposes only.
        
        This value has no semantics. Multiple threads may be given the same name. The
        initial name is set by the constructor.
        """
        return self._thread.name
    
    @name.setter
    def name(self, name):
        self._thread.name = name
    
    @property
    def ident(self):
        """
        Thread identifier of this thread or None if it has not been started.
        
        This is a nonzero integer. Thread identifiers may be recycled when a thread exits 
        and another thread is created. The identifier is available even after the thread 
        has exited.
        """
        return self._thread.ident
    
    @property
    def daemon(self):
        """
        A boolean value indicating whether this thread is a daemon thread.
    
        This must be set before start() is called, otherwise RuntimeError is
        raised. Its initial value is inherited from the creating thread; the
        main thread is not a daemon thread and therefore all threads created in
        the main thread default to daemon = False.
        
        The entire Python program exits when only daemon threads are left.
        """
        return self._thread.daemon
    
    @daemon.setter
    def daemon(self, daemonic):
        self._thread.daemon = daemonic
    
    @property
    def silent(self):
        """
        A boolean value about whether to be silent when this thread is killed.
        
        If this value is False, the thread will use traceback to print out the error
        that shut it down. By default, this value is True. But that means **any** error
        (and not just one created by the kill() method) can silently kill this thread.
        So it is often best to have this value set to False when debugging.
        """
        return self._silent
    
    @silent.setter
    def silent(self, value):
        self._silent = value
    
    @property
    def crashed(self):
        """
        A boolean value to test if the thread died from a crash.
        
        We want to report error messages to students, so we need to distinguish a graceful
        exit from a crash.
        """
        return self._crashed
    
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        """
        This initializer should always be called with keyword arguments.
        
        Parameter group: This value should be None, it is reserved for future extension 
                         when a ThreadGroup class is implemented.
        Precondition: group is None
        
        Parameter target: The callable object to be invoked by the run() method. 
                          Defaults to None, meaning nothing is called.
        Precondition: target is None or callable
        
        Parameter name: The thread name. A default name is assigned if the value is None
        Precondition: name is a str or None
        
        Parameter args: A list or tuple of arguments for the target invocation.
        Precondition: args is a list or tuple
        
        Parameter kwargs: A dictionary of keyword arguments for the target invocation. 
        Precondition: kwargs is a dict
        
        If a subclass overrides the constructor, it must make sure to invoke the base 
        class constructor (SafeThread.__init__()) before doing anything else to the thread.
        """
        self._target = target
        self._args   = args
        self._kwargs = kwargs
        if kwargs is None:
            self._kwargs = {}
        self._thread =  threading.Thread(group=group,target=self._safe_run_,name=name,daemon=daemon)
        self._silent  = True
        self._crashed = False
    
    def __repr__(self):
        """
        Returns the string representation of the underlying thread
        """
        return repr(self._thread)
     
    def start(self):
        """
        Start the thread's activity.
        
        It must be called at most once per thread object. It arranges for the object's 
        run() method to be invoked in a separate thread of control.
        
        This method will raise a RuntimeError if called more than once on the same thread 
        object.

        """
        self._thread.start()
    
    def join(self,timeout=None):
        """
        Wait until the thread terminates.
        
        This blocks the calling thread until the thread whose join() method is
        called terminates -- either normally or through an unhandled exception
        or until the optional timeout occurs.
        
        When the timeout argument is present and not None, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof). As join() always returns None, you must call
        is_alive() after join() to decide whether a timeout happened -- if the
        thread is still alive, the join() call timed out.
        
        When the timeout argument is not present or None, the operation will block 
        until the thread terminates.
        
        A thread can be join()ed many times.
        
        join() raises a RuntimeError if an attempt is made to join the current
        thread as that would cause a deadlock. It is also an error to join() a
        thread before it has been started and attempts to do so raises the same
        exception.
        
        Parameter timeout: The maximum amount of time in seconds to block on the thread
        Precondition: timeout is None or a number
        """
        self._thread.join(timeout)

    def is_alive(self):
        """
        Return whether the thread is alive.
        
        This method returns True just before the run() method starts until just after the 
        run() method terminates. See also the module function enumerate().
        """
        return self._thread.is_alive()
    
    def run(self):
        """
        Method representing the thread's activity.
        
        You may override this method in a subclass. The standard run() method invokes the 
        callable object passed to the object's constructor as the target argument, if any, 
        with sequential and keyword arguments taken from the args and kwargs arguments, 
        respectively.
        """
        try:
            if self._target is not None:
                self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs
    
    def kill(self):
        """
        Safely kills this thread
        
        This method will inject an SystemExit exception into the thread, forcing it to 
        release all locks. This exception will be suppressed by this thread, so that the 
        rest of the program is unharmed if the thread target (or subclass) did not catch 
        it. This method exists primarily to ensure proper resource clean-up. 
        """
        # This code is adapted from https://gist.github.com/liuw/2407154
        thread_id = self._thread.ident
        exception = SystemExit
        
        ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(exception))
        if ret == 0:
            raise ValueError("Invalid thread ID")
        elif ret > 1:
            # If multiple threads got notified, we have a problem. Clean-up
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), ctypes.py_object(None))
            raise SystemError("PyThreadState_SetAsyncExc failed")
    
    def _safe_run_(self):
        """
        Executes the run-method but catches any errors.
        
        This guarantees safe clean-up that does not shut down the rest of the program.
        The offending error will only be logged if silent is false.
        """
        try:
            self.run()
        except:
            self._crashed = True
            if not self.silent:
                traceback.print_exc()


def get_choice(ident):
    """
    Returns a value chosen by this application.
    
    This function waits until the graphical application choses a value (typically via
    user input), and then returns it.  This function will not complete until the value
    is chosen.
    
    Parameter ident: The identity of the entity requesting the value
    Precondition: ident is a non-empty string
    """
    assert type(ident) == str and ident != '', '%s is not a non-empty string' % repr(ident)
    buffer = SharedBuffer()
    buffer.post((ident,False,None))
    buffer.block()
    tag,push,value = buffer.poll()
    if (tag == ident):
        return value
    return None


def set_choice(ident,value):
    """
    Communicates a choice to this application.
    
    The function is called when the code has generated a choice and it wants the 
    graphical application to update the screen to match. This function will not complete 
    until the graphical application has made the change.
    
    Parameter ident: The identity of the entity making the choice
    Precondition: ident is a non-empty string
    
    Parameter value: The choice made
    Precondition; NONE (value can be anything)
    """
    assert type(ident) == str and ident != '', '%s is not a non-empty string' % repr(ident)
    buffer = SharedBuffer()
    buffer.post((ident,True,value))
    buffer.block()
    tag,push,value = buffer.poll()
