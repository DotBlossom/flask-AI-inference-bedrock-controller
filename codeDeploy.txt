import { useState, useRef, useEffect } from "react";
import "../css/Mypage_Cart.css";
import { BsPinAngleFill } from "react-icons/bs";
import { IoMdCloseCircleOutline } from "react-icons/io";
import { FaTrashAlt } from 'react-icons/fa';
import Swal from 'sweetalert2';
import axios from 'axios';
import { useNavigate } from "react-router-dom";

function Mypage_Cart() {
    const [targets, setTargets] = useState([]);
    const [savedTabs, setSavedTabs] = useState([]); // 저장된 탭
    const [activeTab, setActiveTab] = useState(null); // 클릭된 탭의 ID
    const targetBoxRef = useRef(null);
    const [box, setBox] = useState({ top: 0, left: 0, bottom: 0, right: 0 });
    const positionRef = useRef({});
    const [productStock, setProductStock] = useState({});

    // 애니메이션을 위한 refs
    const circleRefs = useRef({});
    const circleLoaderRefs = useRef({});
    const tabRefs = useRef({});

    // 상품 목록을 관리하기 위한 상태 추가
    const [stock, setStock] = useState([]);

    // 선택된 항목을 저장하는 상태
    const [selectedItems, setSelectedItems] = useState([]);
    const [selectAll, setSelectAll] = useState(false); // 전체 선택 상태

    // 삭제 중인 항목들을 추적하는 상태
    const [deletingItems, setDeletingItems] = useState([]);

    // 로딩 상태
    const [isDeleting, setIsDeleting] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    let posX = 0;
    let posY = 0;
    const originalX = useRef(0);
    const originalY = useRef(0);
    const offsetX = useRef(0);
    const offsetY = useRef(0);

    useEffect(() => {
        const updateBox = () => {
            if (targetBoxRef.current) {
                const box = targetBoxRef.current.getBoundingClientRect();
                setBox({
                    top: box.top,
                    left: box.left,
                    bottom: box.top + box.height,
                    right: box.left + box.width,
                });
            }
        };

        // 초기 렌더링 시 box 좌표 계산
        updateBox();

        // 창 크기 변경 시 box 좌표 업데이트
        window.addEventListener("resize", updateBox);

        return () => window.removeEventListener("resize", updateBox);
    }, []);

    // 컴포넌트 마운트 시 API에서 데이터 가져오기
    useEffect(() => {
        const fetchCartItems = async () => {
            setIsLoading(true);
            try {
                const response = await axios.get(`${process.env.REACT_APP_API_BASE_URL_APIgateway}/api/cart/items`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': sessionStorage.getItem('accessToken'),
                    },
                });

                const data = response.data;
                console.log("일반 장바구니 : ", data); // 데이터 로그 찍기

                // 데이터 상태에 저장
                setStock(data);
            } catch (error) {
                console.error("Failed to fetch cart items:", error);
                Swal.fire({
                    title: "장바구니 데이터를 가져오는 데 실패했습니다.",
                    text: error.response?.data?.message || error.message || "",
                    icon: "error",
                    confirmButtonText: "확인",
                    confirmButtonColor: "#754F23",
                    background: "#F0EADC",
                    color: "#754F23",
                });
            } finally {
                setIsLoading(false);
            }
        };

        fetchCartItems();
    }, []);

    // stock 목록에 있는 모든 상품에 대해 재고 정보를 가져옴
    useEffect(() => {
        const fetchProductDetails = async (productCode, itemId) => {
            try {
                const response = await fetch(
                    `${process.env.REACT_APP_API_BASE_URL_APIgateway}/open-api/brand/product/${productCode}`
                );
                if (!response.ok) {
                    throw new Error(`Failed to fetch product details: ${response.status}`);
                }
                const data = await response.json();
                console.log(data);

                setProductStock((prevStock) => ({
                    ...prevStock,
                    [itemId]: data.stock,
                }));
            } catch (error) {
                console.error('Error fetching product details:', error);
            }
        };

        stock.forEach((item) => {
            fetchProductDetails(item.productCode, item.id);
        });
    }, [stock]);

    // 애니메이션 핸들러
    const handleAnimation = async (tabId) => {
        if (
            circleLoaderRefs.current[tabId] &&
            circleRefs.current[tabId] &&
            tabRefs.current[tabId]
        ) {
            circleLoaderRefs.current[tabId].classList.remove('animation');
            circleRefs.current[tabId].classList.remove('animation_circle');
            tabRefs.current[tabId].classList.remove('animation_card');

            setTimeout(() => {
                circleLoaderRefs.current[tabId].classList.add('animation');
                setTimeout(() => {
                    circleRefs.current[tabId].classList.add('animation_circle');
                    tabRefs.current[tabId].classList.add('animation_card');

                    // 애니메이션 완료 후 삭제 요청
                    setTimeout(async () => {
                        try {
                            const accessToken = sessionStorage.getItem('accessToken');
                            await axios.delete(
                                `${process.env.REACT_APP_API_BASE_URL_APIgateway}/api/cart/custom/${tabId}`,
                                {
                                    headers: {
                                        'Authorization': accessToken,
                                    },
                                }
                            );

                            // 탭 삭제 및 상태 업데이트
                            setSavedTabs(prev => prev.filter(tab => tab.id !== tabId));
                            setActiveTab(null);
                            setTargets([]);
                        } catch (error) {
                            console.error("Failed to delete custom cart item:", error);
                            Swal.fire({
                                title: "삭제 실패",
                                text: error.response?.data?.message || error.message || "",
                                icon: "error",
                                confirmButtonText: "확인",
                                confirmButtonColor: "#754F23",
                                background: "#F0EADC",
                                color: "#754F23",
                            });
                        }
                    }, 1000); // 애니메이션 시간과 맞춤
                }, 100);
            }, 100);
        }
    };

    const dragStartHandler = (e) => {
        const img = new Image();
        e.dataTransfer.setDragImage(img, 0, 0);
        posX = e.clientX;
        posY = e.clientY;

        // 드래그 시작 시 요소 id 저장
        e.dataTransfer.setData("targetId", e.target.id || "");
    };

    const dragHandler = (e) => {
        e.target.style.left = `${e.clientX - posX}px`;
        e.target.style.top = `${e.clientY - posY}px`;

        // 마지막 좌표 저장
        positionRef.current[e.target.id] = {
            top: e.clientY - box.top,
            left: e.clientX - box.left,
        };
    };

    const dragEndHandler = (e) => {
        if (box.left < e.clientX && e.clientX < box.right && box.top < e.clientY && e.clientY < box.bottom) {
            const targetId = parseInt(e.target.id);
            const details = stock.find((item) => item.id === targetId);

            if (!details) return;

            const newTargetItem = {
                itemCode: parseInt(e.timeStamp),
                top: e.clientY - box.top,
                left: e.clientX - box.left,
                details: details,
            };

            if (activeTab) {
                setTargets((prevTargets) => [...prevTargets, newTargetItem]);
            } else {
                setTargets((prevTargets) => [...prevTargets, newTargetItem]);
            }

            e.target.style.left = "0px";
            e.target.style.top = "0px";
        }
    };

    const editTabChanges = () => {
        if (activeTab) {
            addTabToSecondBox();
        }
    };

    const targetDragStartHandler = (e, targetId) => {
        e.preventDefault();

        // 배열에서 드래그 중인 아이템을 마지막으로 이동
        setTargets((prevTargets) => {
            const targetIndex = prevTargets.findIndex((target) => target.itemCode === targetId);
            if (targetIndex !== -1) {
                const targetItem = prevTargets[targetIndex];
                const updatedTargets = [...prevTargets];
                updatedTargets.splice(targetIndex, 1);
                updatedTargets.push(targetItem);
                return updatedTargets;
            }
            return prevTargets;
        });

        const targetItem = targets.find((target) => target.itemCode === targetId);
        if (targetItem) {
            const itemElement = document.getElementById(targetId);
            const itemRect = itemElement.getBoundingClientRect();
            const boxRect = targetBoxRef.current.getBoundingClientRect();

            // 마우스 포인터와 아이템의 좌상단 사이의 오프셋 계산
            offsetX.current = e.clientX - itemRect.left;
            offsetY.current = e.clientY - itemRect.top;

            // 아이템의 원래 위치 저장
            originalX.current = targetItem.left;
            originalY.current = targetItem.top;

            const handleMouseMove = (moveEvent) => {
                moveEvent.preventDefault();

                const newLeft = moveEvent.clientX - boxRect.left - offsetX.current;
                const newTop = moveEvent.clientY - boxRect.top - offsetY.current;

                setTargets((prevTargets) =>
                    prevTargets.map((target) =>
                        target.itemCode === targetId
                            ? { ...target, left: newLeft, top: newTop }
                            : target
                    )
                );
            };

            const handleMouseUp = (upEvent) => {
                document.removeEventListener("mousemove", handleMouseMove);
                document.removeEventListener("mouseup", handleMouseUp);

                // 마우스 위치 체크 및 위치 복귀
                const boxRect = targetBoxRef.current.getBoundingClientRect();
                const mouseX = upEvent.clientX;
                const mouseY = upEvent.clientY;

                if (
                    mouseX >= boxRect.left &&
                    mouseX <= boxRect.right &&
                    mouseY >= boxRect.top &&
                    mouseY <= boxRect.bottom
                ) {
                    // target-box 내부에 놓였을 때 위치 유지
                } else {
                    // target-box 외부에 놓였을 때 이전 위치로 복귀
                    setTargets((prevTargets) =>
                        prevTargets.map((target) =>
                            target.itemCode === targetId
                                ? { ...target, left: originalX.current, top: originalY.current }
                                : target
                        )
                    );
                }
            };

            document.addEventListener("mousemove", handleMouseMove);
            document.addEventListener("mouseup", handleMouseUp);
        }
    };

    const deleteTarget = (itemCode) => {
        setTargets((targets) => targets.filter((target) => target.itemCode !== itemCode));
    };

    // 커스텀 장바구니 가져오기 함수 분리
    const fetchCustomCartItems = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_API_BASE_URL_APIgateway}/api/cart/custom`, {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': sessionStorage.getItem('accessToken'),
                },
            });

            const data = response.data;
            console.log("커스텀장바구니 : ", data);
            // 커스텀 장바구니 데이터 상태에 저장
            setCustomCartData(data);
        } catch (error) {
            console.error("Failed to fetch custom cart items:", error);
            Swal.fire({
                title: "커스텀 장바구니 데이터를 가져오는 데 실패했습니다.",
                text: error.response?.data?.message || error.message || "",
                icon: "error",
                confirmButtonText: "확인",
                confirmButtonColor: "#754F23",
                background: "#F0EADC",
                color: "#754F23",
            });
        }
    };

    useEffect(() => {
        fetchCustomCartItems();
    }, []);

    const customCartNameHandler = async (items) => {

        let customCartName;

        const cart_payload = items.map(item => ({
            product_id: item.itemCode,
            product_name: item.productName
        }));


        let body = {
            "custom_cart_id": "100",
            "custom_cart_data": {
                "custom_cart_product_data": [cart_payload]
            }
        }
        console.log(body)
        try {
            const response = await axios.post(
                `https://lambda.dotblossom.today/api/cart/custom/generate`,
                body, {
                headers: {
                    'Content-Type': 'application/json',
                }
            }
            );

            console.log("cart Response:", response.data);
            customCartName = response.data.response_text;
            if (customCartName == null) {
                customCartName = "string01"
            }
        }
        catch (e) {
            // console.log(e);
            // console.log(customCartName)
        }
        return customCartName;
    }

    const addTabToSecondBox = async () => {
        const userId = sessionStorage.getItem('id');
        const accessToken = sessionStorage.getItem('accessToken');

        const items = targets.map(target => ({
            itemCode: target.itemCode,
            top: positionRef.current[target.itemCode]?.top || target.top,
            left: positionRef.current[target.itemCode]?.left || target.left,
            productImage: target.details.productImage,
            productName: target.details.productName
        }));
        const customCartName = await customCartNameHandler(items) || "string_test";

        const payload = {
            userId: userId,
            items: items,
            title: customCartName
            // functions
        };
        // activeTab이 존재하면 id를 추가
        if (activeTab) {
            payload.tabId = activeTab.id;
        }

        Swal.fire({
            title: "AI가 멋진 제목을 지어드릴게요!",
            text: "커스텀 장바구니를 저장 중...",
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        try {

            const response = await axios.post(
                `${process.env.REACT_APP_API_BASE_URL_APIgateway}/api/cart/custom`,
                payload,
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': accessToken,
                    },
                }
            );

            console.log("Custom cart save response:", response.data);

            await fetchCustomCartItems();

            // 저장 후 타겟 및 activeTab 초기화
            setTargets([]);
            setActiveTab(null);
        } catch (error) {
            console.error("Failed to save custom cart items:", error);
            Swal.fire({
                title: "커스텀 장바구니 저장 실패",
                text: error.response?.data?.message || error.message || "",
                icon: "error",
                confirmButtonText: "확인",
                confirmButtonColor: "#754F23",
                background: "#F0EADC",
                color: "#754F23",
            });
        }
    };

    const [customCartData, setCustomCartData] = useState([]);
    // 커스텀 장바구니 가져오기
    useEffect(() => {
        const fetchCustomCartItems = async () => {
            try {
                const response = await axios.get(`${process.env.REACT_APP_API_BASE_URL_APIgateway}/api/cart/custom`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': sessionStorage.getItem('accessToken'),
                    },
                });

                const data = response.data;
                console.log("커스텀장바구니 : ", data);
                // 커스텀 장바구니 데이터 상태에 저장
                setCustomCartData(data);
            } catch (error) {
                console.error("Failed to fetch custom cart items:", error);
                Swal.fire({
                    title: "커스텀 장바구니 데이터를 가져오는 데 실패했습니다.",
                    text: error.response?.data?.message || error.message || "",
                    icon: "error",
                    confirmButtonText: "확인",
                    confirmButtonColor: "#754F23",
                    background: "#F0EADC",
                    color: "#754F23",
                });
            }
        };
        fetchCustomCartItems();
    }, []);

    const showTabInBox = (tab) => {
        const mappedTargets = tab.items.map(item => ({
            itemCode: item.itemCode,
            top: item.top,
            left: item.left,
            details: {
                productName: item.productName,
                productImage: item.productImage,
            },
        }));

        setActiveTab(tab);
        setTargets(mappedTargets);
        console.log("newTab targets:", mappedTargets);
    };

    const closeActiveTab = () => {
        setActiveTab(null);
        setTargets([]);
    };

    // 전체 선택 체크박스 핸들러
    const handleSelectAllChange = () => {
        if (selectAll) {
            setSelectedItems([]); // 전체 해제
        } else {
            setSelectedItems(stock.map(item => item.id));
        }
        setSelectAll(!selectAll);
    };

    // 개별 체크박스 핸들러
    const handleCheckboxChange = (itemId) => {
        setSelectedItems((prevSelectedItems) => {
            const newSelectedItems = prevSelectedItems.includes(itemId)
                ? prevSelectedItems.filter((id) => id !== itemId)
                : [...prevSelectedItems, itemId];
            setSelectAll(newSelectedItems.length === stock.length);
            return newSelectedItems;
        });
    };

    // 수량 업데이트
    const [amount, setAmount] = useState({});

    // API로부터 데이터를 가져온 후 초기 amount 설정
    useEffect(() => {
        const initialAmount = {};
        stock.forEach(item => {
            initialAmount[item.id] = item.quantity;
        });
        setAmount(initialAmount);
    }, [stock]);

    // 수량 변경
    const handleAmountChange = async (id, newAmount) => {
        try {
            const response = await axios.put(
                `${process.env.REACT_APP_API_BASE_URL_APIgateway}/api/cart/items/increase/${id}`,
                {},
                {
                    headers: {
                        'Authorization': sessionStorage.getItem('accessToken'),
                    },
                    params: { quantity: newAmount },
                }
            );

            setAmount((prevAmount) => ({
                ...prevAmount,
                [id]: newAmount,
            }));

            console.log(`Item ${id} quantity ${newAmount} updated successfully:`, response.data);
        } catch (error) {
            console.error(`수량 변경 실패 id - ${id} / quantity - ${newAmount} : `, error);
            Swal.fire({
                title: "수량 변경 실패",
                text: error.response?.data?.message || error.message || "",
                icon: "error",
                confirmButtonText: "확인",
                confirmButtonColor: "#754F23",
                background: "#F0EADC",
                color: "#754F23",
            });
        }
    };

    // 선택된 항목들의 총 가격 계산
    const selectedTotalPrice = stock.reduce((acc, item) => {
        return selectedItems.includes(item.id) ? acc + item.price * (amount[item.id] || item.quantity) : acc;
    }, 0);

    // 선택된 상품 삭제 함수 분리 (추후에 재사용 가능)
    const removeItemsFromCart = async (itemIds) => {
        try {
            // DELETE 요청을 병렬로 처리
            const deletePromises = itemIds.map(async (id) => {
                const response = await axios.delete(`${process.env.REACT_APP_API_BASE_URL_APIgateway}/api/cart/items/${id}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': sessionStorage.getItem('accessToken') || '', // Bearer 제외
                    },
                });

                if (response.status !== 200 && response.status !== 204) { // assuming 200 or 204 is success
                    throw new Error(`Failed to delete item with id ${id}. Status: ${response.status}`);
                }

                return id;
            });

            // 모든 DELETE 요청 완료 대기
            const deletedIds = await Promise.all(deletePromises);
            console.log("Successfully deleted items:", deletedIds);

            // Fade-out 애니메이션 트리거
            setDeletingItems(deletedIds);

            // 애니메이션 시간 후 UI에서 삭제
            setTimeout(() => {
                setStock((prevStock) => prevStock.filter((item) => !deletedIds.includes(item.id)));
                setSelectedItems([]);
                setSelectAll(false);
                setDeletingItems([]);
            }, 500); // 0.5초 후 삭제 (애니메이션 시간과 맞춤)

            return deletedIds;
        } catch (error) {
            console.error("장바구니 항목 삭제 실패", error);
            throw error; // 에러를 상위로 전달
        }
    };

    // 선택된 상품 삭제
    const deleteSelectedItems = async () => {
        if (selectedItems.length === 0) {
            Swal.fire({
                title: "삭제할 항목을 선택해주세요.",
                icon: "warning",
                confirmButtonText: "확인",
                confirmButtonColor: "#754F23",
                background: "#F0EADC",
                color: "#754F23",
            });
            return;
        }

        // 사용자 확인
        const confirmDelete = await Swal.fire({
            title: "선택한 항목들을 삭제하시겠습니까?",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: "삭제",
            cancelButtonText: "취소",
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            background: "#F0EADC",
            color: "#754F23",
        });

        if (!confirmDelete.isConfirmed) return;

        setIsDeleting(true);

        try {
            await removeItemsFromCart(selectedItems);
        } catch (error) {
            // 에러는 removeItemsFromCart 함수 내에서 처리됩니다.
        } finally {
            setIsDeleting(false);
        }
    };

    const handleOutOfStockClick = async (itemId) => {
        const confirmDelete = await Swal.fire({
            title: "해당 상품은 재고가 없습니다.",
            text: "이 상품을 삭제하시겠습니까?",
            icon: "warning",
            showCancelButton: true,
            confirmButtonText: "삭제",
            cancelButtonText: "취소",
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            background: "#F0EADC",
            color: "#754F23",
        });

        if (confirmDelete.isConfirmed) {
            try {
                await removeItemsFromCart([itemId]);
            } catch (error) {
                console.error("Failed to delete item:", error);
            }
        }
    };

    // 주문 함수 수정
    const addOrder = async () => {
        const accessToken = sessionStorage.getItem("accessToken");
        if (!accessToken) {
            Swal.fire({
                title: "로그인이 필요합니다",
                text: "주문을 진행하려면 로그인이 필요합니다.",
                icon: "warning",
                confirmButtonText: "확인",
                confirmButtonColor: "#754F23",
                background: "#F0EADC",
                color: "#754F23",
            });
            return;
        }

        const selectedOrderItems = stock.filter(item => selectedItems.includes(item.id));

        if (selectedOrderItems.length === 0) {
            Swal.fire({
                title: "주문할 항목이 없습니다",
                text: "주문할 상품을 선택해주세요.",
                icon: "warning",
                confirmButtonText: "확인",
                confirmButtonColor: "#754F23",
                background: "#F0EADC",
                color: "#754F23",
            });
            return;
        }

        const orderItemList = selectedOrderItems.map(item => {
            const orderItem = {
                productCode: Number(item.productCode),
                stock: Number(item.quantity),
                color: item.color,
                price: Number(item.price),
                name: item.productName,
                size: item.size,
                thumbnail: item.productImage
            };

            return orderItem;
        });

        const requestData = {
            orderItemList: orderItemList,
        };

        console.log("Order Request Data:", requestData);

        try {
            const response = await axios.post(
                `${process.env.REACT_APP_API_BASE_URL_APIgateway}/api/order`,
                requestData,
                {
                    headers: {
                        Authorization: accessToken,
                        "Content-Type": "application/json",
                    },
                }
            );

            console.log("Order Response:", response.data);

            Swal.fire({
                title: "주문이 완료되었습니다!",
                icon: "success",
                confirmButtonText: "확인",
                confirmButtonColor: "#754F23",
                background: "#F0EADC",
                color: "#754F23",
            });

            // 주문 성공 시 장바구니 항목 삭제 (fade-out 애니메이션 포함)
            await removeItemsFromCart(selectedItems);

        } catch (error) {
            console.error("주문 오류:", error);
            Swal.fire({
                title: "주문 오류",
                text: error.response?.data?.message || "주문 중 오류가 발생했습니다.",
                icon: "error",
                confirmButtonText: "확인",
                confirmButtonColor: "#754F23",
                background: "#F0EADC",
                color: "#754F23",
            });
        }
    };

    const navigate = useNavigate();
    const goToPayPage = () => {
        const selectedOrderItems = stock
            .filter(item => selectedItems.includes(item.id))
            .map(item => ({
                id: item.id,
                productCode: Number(item.productCode),
                stock: Number(item.quantity),
                color: item.color,
                price: Number(item.price),
                name: item.productName,
                size: item.size,
                thumbnail: item.productImage,
            }));

        navigate('/mypages/pay', { state: { products: selectedOrderItems } });
    };

    return (
        <>
            <h2>장바구니</h2>
            <div className="cart-container">
                <div className="targetcart-container">
                    <div className="left-box">
                        <div className="item-box">
                            {stock.map((item) => (
                                <div
                                    key={item.id}
                                    id={item.id}
                                    draggable
                                    onDragStart={dragStartHandler}
                                    onDrag={dragHandler}
                                    onDragEnd={dragEndHandler}
                                    className="item-node"
                                >
                                    {item.productName}
                                </div>
                            ))}
                        </div>

                        <div className="item-box">
                            {savedTabs.map((tab) => (
                                <div
                                    key={tab.id}
                                    ref={el => tabRefs.current[tab.id] = el}
                                    className="item-node saved-tab"
                                    onClick={() => showTabInBox(tab)}
                                >
                                    <div className="saved-tab-content">
                                        {tab.name}
                                    </div>
                                    <div
                                        className="circle"
                                        onClick={() => handleAnimation(tab.id)}
                                        ref={el => circleRefs.current[tab.id] = el}
                                    >
                                        <span className="icon">
                                            <FaTrashAlt />
                                        </span>
                                        <div
                                            className="circle_loader"
                                            ref={el => circleLoaderRefs.current[tab.id] = el}
                                        ></div>
                                    </div>
                                </div>
                            ))}

                            {Array.isArray(customCartData) && customCartData.map((cart) => (
                                <div
                                    key={cart.tabId}
                                    ref={el => tabRefs.current[cart.tabId] = el}
                                    className="item-node saved-tab"
                                    onClick={() => showTabInBox({
                                        id: cart.tabId,
                                        name: cart.title,
                                        items: cart.items
                                    })}
                                >
                                    <div className="saved-tab-content">
                                        {cart.title}
                                    </div>
                                    <div
                                        className="circle"
                                        onClick={() => handleAnimation(cart.tabId)}
                                        ref={el => circleRefs.current[cart.tabId] = el}
                                    >
                                        <span className="icon">
                                            <FaTrashAlt />
                                        </span>
                                        <div
                                            className="circle_loader"
                                            ref={el => circleLoaderRefs.current[cart.tabId] = el}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div ref={targetBoxRef} className="target-box" onDragOver={(e) => e.preventDefault()}>

                        <button
                            className="reset-button"
                            onClick={() => setTargets([])}
                        >
                            <FaTrashAlt />
                        </button>

                        {targets.map((target) => (
                            <div
                                key={target.itemCode}
                                id={target.itemCode}
                                className="target-item"
                                style={{ top: `${target.top}px`, left: `${target.left}px` }}

                            >
                                <div className="icon-row">
                                    <div
                                        className="pin-icon top-center-handle"
                                        onMouseDown={(e) => {
                                            e.preventDefault();
                                            targetDragStartHandler(e, target.itemCode);
                                        }}
                                    >
                                        <BsPinAngleFill />
                                    </div>
                                    <button onClick={() => deleteTarget(target.itemCode)} className="close-delete-button">
                                        <IoMdCloseCircleOutline />
                                    </button>
                                </div>
                                <img src={target.details.productImage} alt={target.details.productName} width="140" />
                                <div>
                                    {target.details.productName}
                                </div>
                            </div>
                        ))}

                        {activeTab && (
                            <div className="active-tab">
                                <button className="cartedit-button" onClick={editTabChanges}>Edit</button>
                                <button className="close-tab-button" onClick={closeActiveTab}>
                                    <IoMdCloseCircleOutline />
                                </button>
                                <p>{activeTab.name}</p>
                            </div>
                        )}

                        <div className="cartsave-button-container">
                            <div id="first" className="cartsave-buttonBox">
                                <button className="cartsave-button" onClick={addTabToSecondBox}>
                                    SAVE
                                </button>
                                <div className="border"></div>
                                <div className="border"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="cart-list-container">
                    <h2>Cart</h2>
                    <p className="delivery-info">
                        * 배송은 2-5일 정도 소요되며 택배사의 상황에 따라 지연될 수 있습니다 *
                    </p>

                    {isLoading ? (
                        <p>로딩 중...</p>
                    ) : (
                        <table className="cart-table">
                            <thead>
                                <tr>
                                    <th>
                                        <input
                                            type="checkbox"
                                            checked={selectAll}
                                            onChange={handleSelectAllChange}
                                        />
                                    </th>
                                    <th>상품 사진</th>
                                    <th>상품 이름</th>
                                    <th>상품 상세</th>
                                    <th>수량</th>
                                    <th>주문금액</th>
                                    <th>배송 정보</th>
                                </tr>
                            </thead>
                            <tbody>
                                {stock.map((item) => {
                                    const isOutOfStock = (productStock[item.id] || 0) === 0;

                                    return (
                                        <tr
                                            key={item.id}
                                            data-id={item.id}
                                            className={`${deletingItems.includes(item.id) ? 'fade-out' : ''} ${isOutOfStock ? 'blurred' : ''}`}
                                            onClick={() => isOutOfStock && handleOutOfStockClick(item.id)}
                                        >
                                            <td>
                                                <input
                                                    type="checkbox"
                                                    checked={selectedItems.includes(item.id)}
                                                    onChange={() => handleCheckboxChange(item.id)}
                                                    disabled={isOutOfStock}
                                                />
                                            </td>
                                            <td>
                                                <img src={item.productImage} alt={item.productName} className="product-image" />
                                            </td>
                                            <td>
                                                <span>{item.productName}</span>
                                            </td>
                                            <td>
                                                <span>{item.size} / {item.color}</span>
                                            </td>
                                            <td>
                                                <select
                                                    value={amount[item.id] || item.quantity}
                                                    onChange={(e) => handleAmountChange(item.id, parseInt(e.target.value))}
                                                    disabled={isOutOfStock}
                                                >
                                                    {[...Array(Math.min(productStock[item.id] || 0, 10)).keys()].map((num) => (
                                                        <option key={num + 1} value={num + 1}>
                                                            {num + 1}
                                                        </option>
                                                    ))}
                                                </select>
                                            </td>
                                            <td>
                                                <span>{item.price.toLocaleString()} KRW</span>
                                            </td>
                                            <td>
                                                무료 택배
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    )}

                    <div className="cart-actions">
                        <button
                            className="action-button"
                            onClick={deleteSelectedItems}
                            disabled={isDeleting}
                        >
                            {isDeleting ? '삭제 중...' : '선택상품 삭제'}
                        </button>
                    </div>

                    <div className="total-summary">
                        <p>총 주문 상품 {selectedItems.length}개</p>
                        <p>
                            {selectedTotalPrice.toLocaleString()} KRW + 0 KRW = {selectedTotalPrice.toLocaleString()} KRW
                        </p>
                    </div>

                    {/* <button className="order-button" onClick={addOrder}>주문하기</button> */}
                    <button
                        className="order-button"
                        onClick={goToPayPage}
                        disabled={selectedItems.length === 0}
                    >
                        주문하기
                    </button>

                    <p className="payment-info">
                        일부 상품은 배송비가 추가될 수 있습니다.
                    </p>
                </div>

            </div>
        </>
    );
}

export default Mypage_Cart;