#!/bin/bash

# Script to rewrite git history with historical changes from the Satzung
# This will create a clean history reflecting the actual document changes

set -e

echo "Creating new git history with historical changes..."

# Backup current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Create a new orphan branch (no history)
git checkout --orphan new-history

# Remove all files from staging
git rm -rf . 2>/dev/null || true

# Initial commit - 25.02.1981 - Eintragung ins Vereinsregister
export GIT_AUTHOR_DATE="1981-02-25T12:00:00"
export GIT_COMMITTER_DATE="1981-02-25T12:00:00"
git commit --allow-empty -m "Eintragung in das Vereinsregister Nr. 1009

Die Eintragung in das Vereinsregister Nr. 1009 wurde heute vollzogen.
Heilbronn, 25. Februar 1981 – Amtsgericht – Registergericht"

# 11.03.1983 / 18.04.1983 - Erste Satzungsänderung
export GIT_AUTHOR_DATE="1983-04-18T12:00:00"
export GIT_COMMITTER_DATE="1983-04-18T12:00:00"
git commit --allow-empty -m "Zusammenfassung der §§ 6 und 7, Ergänzung um § 7, Änderung § 14

Die Mitgliederversammlung vom 11.03.1983 hat die Zusammenfassung der §§ 6 und 7 d. S. zu § 6, 
die Ergänzung um § 7 sowie die Änderung § 14 beschlossen.
Heilbronn, den 18.04.1983 – Amtsgericht – Registergericht"

# 29.03.1985 / 03.07.1985
export GIT_AUTHOR_DATE="1985-07-03T12:00:00"
export GIT_COMMITTER_DATE="1985-07-03T12:00:00"
git commit --allow-empty -m "Ergänzung des § 1

Beschluss vom 29.03.1985
Heilbronn, den 03. Juli 1985 – Amtsgericht – Registergericht"

# 03.04.1987 / 26.06.1987
export GIT_AUTHOR_DATE="1987-06-26T12:00:00"
export GIT_COMMITTER_DATE="1987-06-26T12:00:00"
git commit --allow-empty -m "Änderung in § 16

Beschluss vom 03.04.1987
Heilbronn, den 26.06.1987 – Amtsgericht – Registergericht"

# 22.03.1991 / 21.06.1991
export GIT_AUTHOR_DATE="1991-06-21T12:00:00"
export GIT_COMMITTER_DATE="1991-06-21T12:00:00"
git commit --allow-empty -m "Änderung in den §§ 10, 14, 16 und 17

Beschluss vom 22.03.1991
Heilbronn, den 21.06.1991 – Amtsgericht – Registergericht"

# 27.03.1992 / 14.09.1992
export GIT_AUTHOR_DATE="1992-09-14T12:00:00"
export GIT_COMMITTER_DATE="1992-09-14T12:00:00"
git commit --allow-empty -m "Änderung in § 14

Beschluss vom 27.03.1992
Heilbronn, den 14.09.1992 – Amtsgericht – Registergericht"

# 07.04.1995 / 21.08.1995
export GIT_AUTHOR_DATE="1995-08-21T12:00:00"
export GIT_COMMITTER_DATE="1995-08-21T12:00:00"
git commit --allow-empty -m "Änderung in § 20

Beschluss vom 07.04.1995
Heilbronn, den 21.08.1995 – Amtsgericht – Registergericht"

# 19.04.1996 / 15.05.1997
export GIT_AUTHOR_DATE="1997-05-15T12:00:00"
export GIT_COMMITTER_DATE="1997-05-15T12:00:00"
git commit --allow-empty -m "Änderung in den §§ 1, 5, 6, 10, 11, 14, 16, 21

Beschluss vom 19.04.1996
Heilbronn, den 15.05.1997 – Amtsgericht – Registergericht"

# 11.04.2003 / 13.01.2004
export GIT_AUTHOR_DATE="2004-01-13T12:00:00"
export GIT_COMMITTER_DATE="2004-01-13T12:00:00"
git commit --allow-empty -m "Änderung in den §§ 14, 16, 19, 21

Beschluss vom 11.04.2003
Heilbronn, den 13.01.2004 – Amtsgericht – Registergericht"

# 07.04.2006 / 14.08.2007
export GIT_AUTHOR_DATE="2007-08-14T12:00:00"
export GIT_COMMITTER_DATE="2007-08-14T12:00:00"
git commit --allow-empty -m "Änderung in den §§ 9, 14, 15, 16, 19, 20, 23

Beschluss vom 07.04.2006
Heilbronn, den 14.08.2007 – Amtsgericht – Registergericht"

# 24.04.2009 / 14.07.2009
export GIT_AUTHOR_DATE="2009-07-14T12:00:00"
export GIT_COMMITTER_DATE="2009-07-14T12:00:00"
git commit --allow-empty -m "Änderung in den §§ 2 Abs. 3, 19 Abs. 1

Beschluss vom 24.04.2009
Heilbronn, den 14.07.2009 – Amtsgericht – Registergericht"

# 15.04.2011 / 18.10.2011
export GIT_AUTHOR_DATE="2011-10-18T12:00:00"
export GIT_COMMITTER_DATE="2011-10-18T12:00:00"
git commit --allow-empty -m "Ergänzung § 21; §§ 21ff. entsprechend neu beziffert

Beschluss vom 15.04.2011
Heilbronn, den 18.10.2011 – Amtsgericht – Registergericht"

# 20.04.2012 / 29.01.2013
export GIT_AUTHOR_DATE="2013-01-29T12:00:00"
export GIT_COMMITTER_DATE="2013-01-29T12:00:00"
git commit --allow-empty -m "Ergänzung § 19 Abs. 2 e)

Beschluss vom 20.04.2012
Heilbronn, den 29.01.2013 – Amtsgericht – Registergericht"

# 24.04.2014 - Neufassung
export GIT_AUTHOR_DATE="2014-04-24T12:00:00"
export GIT_COMMITTER_DATE="2014-04-24T12:00:00"
git commit --allow-empty -m "Neufassung der Satzung

Beschluss vom 24.04.2014
Vollständige Neufassung der Vereinssatzung"

# Now add all current files
git checkout $CURRENT_BRANCH -- .
git add .

# 21.04.2023 / 04.07.2023
export GIT_AUTHOR_DATE="2023-07-04T12:00:00"
export GIT_COMMITTER_DATE="2023-07-04T12:00:00"
git commit -m "Änderung in Punkt 3.2.1, 3.2.4, 3.1-3.3., 3.7.2, Ergänzung in Punkt 3.10.2-4, 5.1-3

Beschluss vom 21.04.2023
Heilbronn, den 04.07.2023 – Amtsgericht – Registergericht"

# 12.04.2024 / 11.07.2024
export GIT_AUTHOR_DATE="2024-07-11T12:00:00"
export GIT_COMMITTER_DATE="2024-07-11T12:00:00"
git commit --allow-empty -m "Ergänzung Punkt 3.10.10

Beschluss vom 12.04.2024
Heilbronn, den 11.07.2024 – Amtsgericht – Registergericht"

# Unset the date variables
unset GIT_AUTHOR_DATE
unset GIT_COMMITTER_DATE

echo ""
echo "New history created successfully!"
echo ""
echo "To apply this new history:"
echo "1. Review the new history: git log --oneline"
echo "2. If satisfied, replace main branch: git branch -D main && git branch -m new-history main"
echo "3. Force push to remote: git push -f origin main"
echo ""
echo "WARNING: This will rewrite history. Make sure all team members are aware!"
