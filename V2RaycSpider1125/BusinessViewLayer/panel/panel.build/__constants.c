
#include "nuitka/prelude.h"
#include "structseq.h"

// Global constants storage
PyObject *global_constants[69];

// Sentinel PyObject to be used for all our call iterator endings. It will
// become a PyCObject pointing to NULL. It's address is unique, and that's
// enough for us to use it as sentinel value.
PyObject *_sentinel_value = NULL;

PyObject *Nuitka_dunder_compiled_value = NULL;

// We need to make sure this is local to the package, or else it will
// be taken from any external linkage.
#if defined(_NUITKA_MODULE) && !defined(_NUITKA_CONSTANTS_FROM_RESOURCE) && !defined(__cplusplus)
const unsigned char constant_bin[0];
#endif

#ifdef _NUITKA_STANDALONE
extern PyObject *getStandaloneSysExecutablePath(PyObject *basename);
#endif

static void _createGlobalConstants(void) {
    // The empty name means global.
    loadConstantsBlob(&global_constants[0], "", 69);

#if _NUITKA_EXE
    /* Set the "sys.executable" path to the original CPython executable or point to inside the
       distribution for standalone. */
    PySys_SetObject(
        (char *)"executable",
#ifndef _NUITKA_STANDALONE
        global_constants[67]
#else
        getStandaloneSysExecutablePath(global_constants[67])
#endif
    );

#ifndef _NUITKA_STANDALONE
    /* Set the "sys.prefix" path to the original one. */
    PySys_SetObject(
        (char *)"prefix",
        global_constants[68]
    );

    /* Set the "sys.prefix" path to the original one. */
    PySys_SetObject(
        (char *)"exec_prefix",
        global_constants[68]
    );


#if PYTHON_VERSION >= 300
    /* Set the "sys.base_prefix" path to the original one. */
    PySys_SetObject(
        (char *)"base_prefix",
        global_constants[68]
    );

    /* Set the "sys.exec_base_prefix" path to the original one. */
    PySys_SetObject(
        (char *)"base_exec_prefix",
        global_constants[68]
    );

#endif
#endif
#endif

    static PyTypeObject Nuitka_VersionInfoType;

    // Same fields as "sys.version_info" except no serial number.
    static PyStructSequence_Field Nuitka_VersionInfoFields[] = {
        {(char *)"major", (char *)"Major release number"},
        {(char *)"minor", (char *)"Minor release number"},
        {(char *)"micro", (char *)"Micro release number"},
        {(char *)"releaselevel", (char *)"'alpha', 'beta', 'candidate', or 'release'"},
        {0}
    };

    static PyStructSequence_Desc Nuitka_VersionInfoDesc = {
        (char *)"__nuitka_version__",                                    /* name */
        (char *)"__compiled__\\n\\nVersion information as a named tuple.", /* doc */
        Nuitka_VersionInfoFields,                                        /* fields */
        4
    };

    PyStructSequence_InitType(&Nuitka_VersionInfoType, &Nuitka_VersionInfoDesc);

    Nuitka_dunder_compiled_value = PyStructSequence_New(&Nuitka_VersionInfoType);
    assert(Nuitka_dunder_compiled_value != NULL);

    PyStructSequence_SET_ITEM(Nuitka_dunder_compiled_value, 0, PyInt_FromLong(0));
    PyStructSequence_SET_ITEM(Nuitka_dunder_compiled_value, 1, PyInt_FromLong(6));
    PyStructSequence_SET_ITEM(Nuitka_dunder_compiled_value, 2, PyInt_FromLong(10));

    PyStructSequence_SET_ITEM(Nuitka_dunder_compiled_value, 3, Nuitka_String_FromString("candidate"));

    // Prevent users from creating the Nuitka version type object.
    Nuitka_VersionInfoType.tp_init = NULL;
    Nuitka_VersionInfoType.tp_new = NULL;


}

// In debug mode we can check that the constants were not tampered with in any
// given moment. We typically do it at program exit, but we can add extra calls
// for sanity.
#ifndef __NUITKA_NO_ASSERT__
void checkGlobalConstants(void) {
// TODO: Ask constant code to check values.

}
#endif

void createGlobalConstants(void) {
    if (_sentinel_value == NULL) {
#if PYTHON_VERSION < 300
        _sentinel_value = PyCObject_FromVoidPtr(NULL, NULL);
#else
        // The NULL value is not allowed for a capsule, so use something else.
        _sentinel_value = PyCapsule_New((void *)27, "sentinel", NULL);
#endif
        assert(_sentinel_value);

        _createGlobalConstants();
    }
}

