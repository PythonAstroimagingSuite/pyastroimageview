echo "BUILD SCRIPT RUNNING"

ASTROPKG="pyastroimageview"
BACKPKG="pyastrobackend"

mkdir -p ${PREFIX}/Lib/site-packages/${ASTROPKG}
mkdir -p ${PREFIX}/Lib/site-packages/${BACKPKG}
mkdir -p ${PREFIX}/Scripts

cp scripts/${ASTROPKG}_main.py ${PREFIX}/Scripts/
cp -ar ${ASTROPKG} ${PREFIX}/Lib/site-packages/${ASTROPKG}
cp -ar ${BACKPKG} ${PREFIX}/Lib/site-packages/${BACKPKG}

# put version in sources so we can report it when program is run
echo VERSION=\'${PKG_VERSION}-py${CONDA_PY}${GIT_DESCRIBE_HASH}_${GIT_DESCRIBE_NUMBER}\' >> ${PREFIX}/Lib/site-packages/${ASTROPKG}/build_version.py
