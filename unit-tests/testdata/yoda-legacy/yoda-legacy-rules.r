# \brief Retrieve the client zone name.
#
# \param[out] zoneName
#
uuClientZone(*zoneName) {
    *zoneName = $rodsZoneClient;
}

uuClientFullName() = "$userNameClient#$rodsZoneClient";

# \brief Wrapper around uuClientFullName. Enables uuClientFullName to be called
#        from the Python iRODS client
#
# \param[out] fullName
#
uuClientFullNameWrapper(*fullName) {
    *fullName = uuClientFullName();
}

# \brief Check if a group category exists.
#
# \param[in]  categoryName
# \param[out] exists
#
uuGroupCategoryExists(*categoryName, *exists) {
        *exists = false;
        foreach (
                *row in
                SELECT META_USER_ATTR_VALUE
                WHERE  USER_TYPE            = 'rodsgroup'
                  AND  META_USER_ATTR_NAME  = 'category'
                  AND  META_USER_ATTR_VALUE = '*categoryName'
        ) {
                *exists = true;
        }
}
