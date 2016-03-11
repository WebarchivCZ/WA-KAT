DB    L NKC01
SYSID L 0
FMT   L SE
LDR   L -----nai-a22------i-4500
BAS   L $$a01
BAS   L $$aWAR
BAS   L $$aSML
001   L web***********
003   L CZ-PrNK
006   L m-----o--d--------
007   L cr-cn-
008   L ******c{{from_year}}{{to_year}}xr--x-w-o----*0---b2cze--
022   L $$a{{!issn}}
040   L $$aABA001$$bcze$$erda
0410  L $$a{{!language}}
043   L $$a $$b $$2 
045   L $$a 
072 7 L $$a{{conspect["mdt"]}}$$x{{conspect["name"]}}$$2Konspekt$$9{{conspect["conspect_id"]}}
% if conspect.get("en_name") and conspect.get("ddc"):
072 9 L $$a{{conspect["ddc"]}}$$x{{conspect["en_name"]}}$$2Conspectus$$9{{conspect["conspect_id"]}}
% end
% for rec in mdt:
080   L $$a{{rec["mdt"]}}$$2{{rec["mrf"]}}
% end
080   L $$uwww dokumenty$$a(0.034.2)004.738.12$$2MRF
% if author:
{{!serialized_author}}
% else:
1001  L $$a $$d $$4 
1102  L $$a $$b 
% end
1112  L $$a $$d $$c 
% if issn:
222 0 L $$a{{title}}$$b 
% end
245*0 L $$a{{title}}$$b{{subtitle}}
246** L $$a 
264 1 L $$a{{place}}$$b{{publisher or author.get("name", " ")}}$$c{{creation_date}}
300   L $$a1 online zdroj
310   L $$a{{periodicity}}
336   L $$atext$$btxt$$2rdacontent
337   L $$apočítač$$bc$$2rdamedia
338   L $$aonline zdroj$$bcr$$2rdacarrier
5880  L $$aPopsáno podle celého zdroje; název z titulní obrazovky (verze z {{time.strftime("%d.%m.%Y")}})
520   L $$a{{annotation}}
60017 L $$a 
61027 L $$a 
61127 L $$a 
648 7 L $$a 
% for keyword in cz_keywords:
65007 L $$a{{keyword["zahlavi"]}}$$7{{keyword["uid"]}}$$2{{keyword["zdroj"]}}
% end 
% for keyword in en_keywords:
65009 L $$a{{keyword["zahlavi"]}}$$2{{keyword["zdroj"]}}
% end
651 7 L $$a 
651 9 L $$a 
655 7 L $$awww dokumenty$$7fd186892
655 9 L $$uwww dokumenty$$awww documents
7001  L $$a $$4 
7102  L $$a 
7112  L $$a 
85640 L $$u{{url}}$$qtext/html$$4N
85640 L $$uhttp://wayback.webarchiv.cz/wayback/{{url}}$$qtext/html$$zarchivní verze stránek$$4N
929   L $$aText
930   L $$acop.
NKC   L $$aČNB-w
IST1  L $$awz********$$b****
