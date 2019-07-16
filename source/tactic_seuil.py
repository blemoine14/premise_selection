from predictionManager import *
from zipper_utils import *
import itertools
from shutil import copyfile

def tactic_seuil(predictionManager,zf_dir_path,list_of_lemme,min_seuil=1e-7,seuil=0.9) :

    if list_of_lemme is None :
        list_of_lemme = predictionManager.dataManager.th_names
    
    if not(list_of_lemme and seuil > min_seuil) : #possède au moins un élément
        return []
    
    global zipper_exec_time
    print("size_of_echantillon =",len(list_of_lemme))
    print("starting")
    
    print("create files")

    copyfile(pm.dataManager.data_dir+pm.dataManager.rew_type_file, zf_dir_path+pm.dataManager.rew_type_file)

    for chapter in predictionManager.dataManager.struct_dict :
        for lemme in predictionManager.dataManager.struct_dict[chapter] :
            if lemme in list_of_lemme :
	            zf_file=zf_dir_path+predictionManager.dataManager.get_chapter(lemme)+"/"+lemme+".zf"
	            predictionManager.th_name_pred_seuil_to_zf_file(lemme,zf_file,seuil=seuil)
                
    print("file created")
                
    threads=[]

    for chapter in predictionManager.dataManager.struct_dict :

        zipper_exec_time[chapter]=dict()

        for lemme in predictionManager.dataManager.struct_dict[chapter] :
            if lemme in list_of_lemme :
                threads.append(Zipperposition(zf_dir_path,chapter,lemme))

    for i in range(len(threads)):
        with semZ :
            threads[i].start()

    for i in range(len(threads)):
        threads[i].join()
    
    done,notdone,gaveup,ressourceout,timeout = get_zipper_stat(zipper_exec_time)
    
    print("Seuil done : "+str(seuil))
    print(zipper_stat(done,notdone,gaveup,ressourceout,timeout))

    data_list = tactic_seuil(predictionManager,zf_dir_path,notdone,min_seuil,seuil/1.2)
    return [[seuil,done,notdone,gaveup,ressourceout,timeout]]+data_list


def display_data(datas) :
    seuil=[]
    done=[]
    notdone=[]
    gaveup=[]
    ressourceout=[]
    timeout=[]
    for i in range(len(datas)) :
        seuil.append(datas[i][0])
        done.append(len(list(itertools.chain.from_iterable([data[1] for data in datas[:(i+1)]]))))
        notdone.append(len(datas[i][2]))
        gaveup.append(len(datas[i][3]))
        ressourceout.append(len(datas[i][4]))
        timeout.append(len(datas[i][5]))
    x=seuil
    y1=done
    y2=notdone
    y3=gaveup
    y4=ressourceout
    y5=timeout
    plt.plot(x,y1,linewidth=2.0,label = "done")
    plt.xlim(x[0]+0.01,x[-1]-0.01)
    plt.legend()
    plt.show()
    print(done[len(done)-1],"/",(done[len(done)-1]+notdone[len(notdone)-1]))
    print(datas[len(datas)-1][2])
    return list(itertools.chain.from_iterable([data[1] for data in datas[:(i+1)]]))


if __name__ == "__main__":
	if len(sys.argv) != 4 :
		print("Prend en parametre :\n dossier contenant la sauvegarde du reseau\n dossier de destination des fichiers .zf\n fichier de sauvegarde des donnees de la tactique\n fichier contenant la liste des theoremes sur lequel la tactique sera appliquee (par defaut : None pour traiter tout les theoremes)\n seuil_initial (par defaut : 0.9)\n seuil_minimal (par defaut : 1e-7))")
	else :
		dm=DataManager(data_dir="../datas/",rew_def_file="rew_def.zf",ax_th_def_file="ax_th_def.zf",struct_file="config_struct.json",rew_type_list="rew_type.json",rew_type_file="rew_type.zf")
		res=Reseau()
		res.load(sys.argv[1])
		pm=PredictionManager(dm,res)
		datas=tactic_seuil(pm,sys.argv[2],None,min_seuil=1e-7,seuil=0.9)
		with open(sys.argv[3], "wb") as fp:
    			pickle.dump(datas, fp)
		done=display_data(datas)
