import pytest
from output_validation.utils.QiQuery import QiQuery

class TestQiQuery:


    def testInit(self):
        qiQ_1 = QiQuery('','','','*')
        assert not qiQ_1.identifyingColumns
        assert not qiQ_1.quasiIdentifyingColumns
        assert not qiQ_1.sensitiveColumns
        assert qiQ_1.blindSymbol == '*'
        assert qiQ_1.ALLBLIND == '1 = 1'
        assert qiQ_1.NOBLIND == '1 = 1'
        qiQ_2 = QiQuery('asd','bsd, csd, dsd','','')
        assert qiQ_2.identifyingColumns == 'asd'
        assert qiQ_2.quasiIdentifyingColumns == 'bsd, csd, dsd'
        assert not qiQ_2.sensitiveColumns
        assert qiQ_2.blindSymbol == '*'
        assert qiQ_2.ALLBLIND == "bsd = '*' AND csd = '*' AND dsd = '*'"
        assert qiQ_2.NOBLIND == "bsd IS DISTINCT FROM '*' OR csd IS DISTINCT FROM '*' OR dsd IS DISTINCT FROM '*'"
        qiQ_3 = QiQuery('id','qid','sens',"'")
        assert qiQ_3.identifyingColumns == 'id'
        assert qiQ_3.quasiIdentifyingColumns == 'qid'
        assert qiQ_3.sensitiveColumns == 'sens'
        assert qiQ_3.blindSymbol == "*"
        assert qiQ_3.ALLBLIND == "qid = '*'"
        assert qiQ_3.NOBLIND == "qid IS DISTINCT FROM '*'"


    def testStringToList(self):
        qiQ_1 = QiQuery('id','qid','sens','x')
        expected1 = ['first', 'second', 'third', 'fourth']
        liststring1 = '             first,  second       , third, fourth  '
        computed1 = qiQ_1.commaSeparatedColumnsAsList(liststring1)
        expected2 = []
        liststring2 = '                 '
        computed2 = qiQ_1.commaSeparatedColumnsAsList(liststring2)
        expected3 = []
        liststring3 = ''
        computed3 = qiQ_1.commaSeparatedColumnsAsList(liststring3)
        expected4 = ['t_es_tval_..!_?_u_e_---__ö']
        liststring4 = 't es tval ..! ? u e ---_             ö'
        computed4 = qiQ_1.commaSeparatedColumnsAsList(liststring4)
        expected5 = ['t1', 't2...=="+', 't3','t4t5','t6']
        liststring5 = ',,t1,,,t2...=="+,,,t3,t4t5,,,,,,,t6'
        computed5 = qiQ_1.commaSeparatedColumnsAsList(liststring5)
        expected6 = ['column_name_with_spaces', 'another_one', 'just_one']
        liststring6 = 'column name with             spaces, another             one, just one       ,,,,'
        computed6 = qiQ_1.commaSeparatedColumnsAsList(liststring6)
        assert expected6 == computed6
        assert expected1 == computed1
        assert expected2 == computed2
        assert expected3 == computed3
        assert expected4 == computed4
        assert expected5 == computed5


    def testQiQueryBuild(self):
        qiQ_1 = QiQuery('','','','')
        expected1 = ''
        computed1 = qiQ_1.createQueryString(qiQ_1.AND, ' > 1')
        with pytest.raises(Exception):
            qiQ_1.quasiIdentifyingColumns = 'one, two, three'
        qiQ_2 = QiQuery('','one, two, three','','')
        expected2 = 'one > 1 AND two > 1 AND three > 1'
        computed2 = qiQ_2.createQueryString(qiQ_2.AND, ' > 1')
        expected3 = '1 = 1'
        computed3 = qiQ_2.createQueryString('whatever', 'some condition')
        assert expected1 == computed1
        assert expected2 == computed2
        assert expected3 == computed3


    def testDictToQUery(self):
        qiQ_1 = QiQuery('','','','')
        mydict1 = {'key1' : 5, 'key2' : 1203924, 'key3': -59.01}
        expected1 = 'key1 = 5 OR key2 = 1203924 OR key3 = -59.01'
        computed1 = qiQ_1.dictToQueryString(qiQ_1.OR, '=', mydict1)
        mydict2 = {'key1' : 'value1', 'key2' : 'value2', 'key3': '       noisyVal_uE!333     _?'}
        expected2 = "key1 != 'value1' AND key2 != 'value2' AND key3 != '       noisyVal_uE!333     _?'"
        computed2 = qiQ_1.dictToQueryString(qiQ_1.AND, '!=', mydict2)
        mydict3 = {'key1' : 'value1', 'key2' : 'value2', 'key3': 'value3'}
        expected3 = "1 = 1"
        computed3 = qiQ_1.dictToQueryString('somethingnotallowed', '>=', mydict3)
        assert expected1 == computed1
        assert expected2 == computed2
        assert expected3 == computed3
