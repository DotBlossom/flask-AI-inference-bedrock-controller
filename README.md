
## descriptions


![스크린샷 2024-12-14 083350](https://github.com/user-attachments/assets/a522a54b-3fc2-407a-91ea-60d3a63e7710)

![스크린샷 2024-12-14 083357](https://github.com/user-attachments/assets/d997babb-bf7d-4905-949c-ae3044492252)
![스크린샷 2024-12-14 083404](https://github.com/user-attachments/assets/0ed9c16c-fd1d-4f58-b11d-3a2cc7fb0375)
![스크린샷 2024-12-14 083411](https://github.com/user-attachments/assets/9974c0f6-8f2c-40b8-9040-a5d016d9f8c6)
![스크린샷 2024-12-14 083140](https://github.com/user-attachments/assets/2fa6d263-1fd8-4692-80ec-9088305dc9d9)


## front fatching 전략
    - bedrock custom-cart async result func : var = await func in succ
    - product add : axios main async - next useRef useEffect
    - make "body" object to convert any type of datastreams.
    - function of propagation of actions : await syncer

## P,N, A boundary Indexing
    
    N = negative
    Lx = Reg number of B
    fn = features of categorize
    B(u,l).fn = u,l boundary
    
    
    N = T - (A - P) / Lx
    B(u,l)f1 = [0.1 , Pi({x,n}, 1->k) x / Ly 

    feature selector : Dominent[1] , Sub(W) = f(k-1)[0.01, 0.001 .. ]

    
    B(u,l)f1 = [0.1 , Pi({x,n}, 1->k) x / Ly1 
    B(u,l)f2 = [B(l)f1 , Pi({x,n}, 1->k) x / Ly2]
    ..
    B(u,l)fn = [B(l)fn , Pi({x,n}, 1->k) x / Lyn]

    S(B(u,l)f(k)) = key indexing Boundary values.

    or Cx(B(u,l)f(k)) -> n filters. of parallel (Vector N d)

    ver2.
    multivar_ranker(operated by type of LLM res)
    rf = dominent_selector + S{(1,argmax(k:3), w =: 0.001w} w(k) * sub_selector(k)}
    re = rf * t(pre) , d = 16
    v(re) = 16 innerproductor, if thrs >= k , merge types
    v(re(n)) * v(re(u)) : pretrained input selector of thrs

## migrate to fastAPI 
    https://github.com/DotBlossom/ai-pref-pipeline-fastAPI