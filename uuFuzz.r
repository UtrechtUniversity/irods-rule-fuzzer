# \brief Store a log message in the server log for marking fuzzing-related messages
#
# \param[in] logmarker    an arbitrary string to be used for marking the start or end of
#                         a fuzzing invocation. This string is stored in the server log, so
#                         that an operator can differentiate between log messages generated
#                         by different fuzzing actions
# \param[out] returnvalue Should always be "OK". Can also be used to check whether iRODS is still
#                         available.
fuzzCheck(*logmarker, *returnvalue) {
        *returnvalue = "OK";
        writeLine("serverLog","Fuzzing marker: *logmarker");
}
