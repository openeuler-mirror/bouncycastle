%define tag r1rv61
%define class_name org.bouncycastle.jce.provider.BouncyCastleProvider
%define jdk_dir build/artifacts/jdk1.5
%define java_sec_dir %{_sysconfdir}/java/security/security.d
%define suffix_name security/classpath.security

Name:             bouncycastle
Version:          1.61
Release:          4
Summary:          A Java implementation of cryptographic algorithms
License:          MIT
URL:              http://www.bouncycastle.org
Source0:          https://github.com/bcgit/bc-java/archive/%{tag}.tar.gz
Source1:          http://repo1.maven.org/maven2/org/bouncycastle/bcmail-jdk15on/%{version}/bcmail-jdk15on-%{version}.pom
Source2:          http://repo1.maven.org/maven2/org/bouncycastle/bcpg-jdk15on/%{version}/bcpg-jdk15on-%{version}.pom
Source3:          http://repo1.maven.org/maven2/org/bouncycastle/bcpkix-jdk15on/%{version}/bcpkix-jdk15on-%{version}.pom
Source4:          http://repo1.maven.org/maven2/org/bouncycastle/bcprov-jdk15on/%{version}/bcprov-jdk15on-%{version}.pom
Source5:          http://repo1.maven.org/maven2/org/bouncycastle/bctls-jdk15on/%{version}/bctls-jdk15on-%{version}.pom
Patch6000:        CVE-2019-17359.patch

BuildRequires:    ant ant-junit aqute-bnd javamail javapackages-local
Requires(post):   javapackages-tools
Requires(postun): javapackages-tools

BuildArch:        noarch

Provides:         bcprov = %{version}-%{release}
Provides:         %{name}-pkix
Provides:         %{name}-pg
Provides:         %{name}-mail
Provides:         %{name}-tls
Provides:         %{name}-javadoc
Provides:         %{name}-pkix-javadoc = %{version}-%{release}
Provides:         %{name}-pg-javadoc = %{version}-%{release}
Provides:         %{name}-mail-javadoc = %{version}-%{release}
Obsoletes:        %{name}-pkix
Obsoletes:        %{name}-pg
Obsoletes:        %{name}-mail
Obsoletes:        %{name}-tls
Obsoletes:        %{name}-javadoc
Obsoletes:        %{name}-pkix-javadoc < %{version}-%{release}
Obsoletes:        %{name}-pg-javadoc < %{version}-%{release}
Obsoletes:        %{name}-mail-javadoc < %{version}-%{release}

%description
The package is organised so that it contains a light-weight API suitable for
use in any environment (including the newly released J2ME) with the additional
infrastructure to conform the algorithms to the JCE framework.


%prep
%autosetup -n bc-java-%{tag} -p1

find . -type f -name "*.class" -delete
find . -type f -name "*.jar" -delete

sed -i -e '/<javadoc/aadditionalparam="-Xdoclint:none" encoding="UTF-8"' \
       -e '/<javac/aencoding="UTF-8"' ant/bc+-build.xml

cp -p %{SOURCE1} bcmail.pom
cp -p %{SOURCE2} bcpg.pom
cp -p %{SOURCE3} bcpkix.pom
cp -p %{SOURCE4} bcprov.pom
cp -p %{SOURCE5} bctls.pom

%build
ant -f ant/jdk15+.xml \
  -Dactivation.jar.home= \
  -Dmail.jar.home=$(build-classpath javax.mail) \
  -Djunit.jar.home=$(build-classpath junit) \
  -Drelease.debug=true \
  clean build-provider build

cat > bnd.bnd <<EOF
-classpath=bcprov.jar,bcpkix.jar,bcpg.jar,bcmail.jar,bctls.jar
Export-Package: *;version=%{version}
EOF

for kind in bcprov bcpkix bcpg bcmail bctls ; do
  bnd wrap -b $kind -v %{version} -p bnd.bnd -o $kind.jar %{jdk_dir}/jars/$kind-jdk15on-*.jar

  %mvn_file ":$kind-jdk15on" $kind
  %mvn_package ":$kind-jdk15on" $kind
  %mvn_alias ":$kind-jdk15on" "org.bouncycastle:$kind-jdk16" "org.bouncycastle:$kind-jdk15"
  %mvn_artifact $kind.pom $kind.jar
done

rm -rf %{jdk_dir}/javadoc/lcrypto

%install
install -d -m 755 %{buildroot}%{java_sec_dir}
touch %{buildroot}%{java_sec_dir}/2000-%{class_name}

%mvn_install -J %{jdk_dir}/javadoc

%post
{
  suffix=%{suffix_name}
  class_secfiles="/usr/lib/$suffix /usr/lib64/$suffix"

  for secfile in $class_secfiles
  do
    [ -f "$secfile" ] || continue

    sed -i '/^security\.provider\./d' "$secfile"

    num=0
    for provider in $(ls %{java_sec_dir})
    do
      num=$((num + 1))
      echo "security.provider.${num}=${provider#*-}" >> "$secfile"
    done
  done
} || :

%postun
if [ "$1" -eq 0 ] ; then

  {
    suffix=%{suffix_name}
    class_secfiles="/usr/lib/$suffix /usr/lib64/$suffix"

    for secfile in $class_secfiles
    do
      [ -f "$secfile" ] || continue

      sed -i '/^security\.provider\./d' "$secfile"

      num=0
      for provider in $(ls %{java_sec_dir})
      do
        num=$((num + 1))
        echo "security.provider.${num}=${provider#*-}" >> "$secfile"
      done
    done
  } || :

fi

%files
%doc docs/ core/docs/ *.html
%doc %{_javadocdir}/%{name}
%license %{jdk_dir}/bcprov-jdk15on-*/LICENSE.html
%{_datadir}/maven-metadata/*
%{_javadir}/*
%{_mavenpomdir}/*
%{java_sec_dir}/2000-%{class_name}

%changelog
* Wed Feb 12 2020 Shuaishuai Song <songshuaishuai2@huawei.com> - 1.61-4
- remove script

* Thu Dec 26 2019 zhujunhao <zhujunhao5@huawei.com> - 1.61-3
- Type:cves
- ID:CVE-2019-17359
- SUG:restart
- DESC:fix CVE-2019-17359

* Tue Dec 10 2019 huyan <hu.huyan@huawei.com> - 1.61-2
- Package Initialization
