def main():
    #모든 것의 시작
    while 1:
        if point_full <= 0:
            print("가여운 고양이는 무지개별로 떠났습니다.")
            print("하지만 삶은 본래 무상한 것이지요.")
            print("모든 것은 무상하지만 인연과 사랑은")
            print("     공허속에도 머무릅니다.")
            break
        elif point_full >= 200:
            print("나는 도시의 골목대장이 되었다냥!")
            print("고양이는 행복하게 살았습니다 ^^")
            print("       게임 clear     ")
            break


        print("길에 버려진 불쌍한 고양이, 도시에서 살아남아보자!")
        print("포만감이 200이 되면 살아남습니다.")
        print("포만감이 0이 되면 죽습니다.")
        print(f"현재 포만감 : {point_full}")
        print("어디로 이동할까? 1. 학교 2. 숲")
        move = int(input())

        match move:
            case 1:
                school()
            case 2:
                forest()
            case _:
                print("선택지 안에서 선택하라냥!")
                continue

        


def school_act(act1, lucky):
    global point_full
    if act1 == 1 and lucky >=0.5:
        print("운좋게 생선을 얻었다냥! 포만감이 상승합니다.")
        point_full += 20
    else:
        print("먹을게 없었다냥 ㅠㅠ 지치기만해서 포만감이 떨어집니다.")
        point_full -=20
        

def school():
    while 1:
        lucky = random.random()
        print("어떻게 할까? 1. 쓰레기통을 뒤진다. 2. 학교에서 나간다.")
        act1 = int(input())

        match act1:
            case 1:
                school_act(act1, lucky)
            case 2:
                break


def forest():
    while 1:
        lucky = random.random()
        print("어떻게 할까? 1. 물고기를 사냥한다. 2. 숲에서 나간다.")
        act1 = int(input())

        match act1:
            case 1:
                forest_act(act1, lucky)
            case 2:
                break

def forest_act(act1, lucky):
    global point_full
    if act1 == 1 and lucky >=0.5:
        print("운좋게 생선을 얻었다냥! 포만감이 상승합니다.")
        point_full += 20
    else:
        print("사냥에 실패했다냥 ㅠㅠ 지치기만해서 포만감이 떨어집니다.")
        point_full -=20

main()