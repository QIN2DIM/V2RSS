#ifndef __NUITKA_CALLS_H__
#define __NUITKA_CALLS_H__

extern PyObject *CALL_FUNCTION_WITH_ARGS1(PyObject *called, PyObject **args);
extern PyObject *CALL_FUNCTION_WITH_ARGS2(PyObject *called, PyObject **args);
extern PyObject *CALL_FUNCTION_WITH_ARGS3(PyObject *called, PyObject **args);
extern PyObject *CALL_FUNCTION_WITH_ARGS4(PyObject *called, PyObject **args);
extern PyObject *CALL_FUNCTION_WITH_ARGS5(PyObject *called, PyObject **args);
extern PyObject *CALL_METHOD_WITH_ARGS1(PyObject *source, PyObject *attr_name, PyObject **args);
extern PyObject *CALL_METHOD_WITH_ARGS2(PyObject *source, PyObject *attr_name, PyObject **args);
#endif

