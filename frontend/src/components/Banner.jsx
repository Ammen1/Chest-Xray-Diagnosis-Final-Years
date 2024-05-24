import React from 'react';
import Fade from 'react-reveal/Fade';
import { useNavigate } from 'react-router-dom';
import { Button } from 'flowbite-react';
import Lottie from 'lottie-react';
import animationData from '../assets/Animation .json';

const Banner = () => {
    const history = useNavigate();
    const currentYear = new Date().getFullYear();

    return (
        <section className="container max-w-screen-xl px-6 mx-auto mb-20">
            <div className="grid grid-cols-1 gap-10 py-12 md:grid-cols-2 lg:grid-cols-2">
                <Fade left>
                    <div className="flex flex-col justify-center order-1 h-full space-y-6 lg:order-1">

                        <div className="flex flex-col mt-10">
                            {/* <img className="w-56" src="../../../assets/banner/x-ray.png" alt="X-ray" /> */}
                            <h1 className="text-3xl font-semibold leading-relaxed text-gray-700 poppins lg:text-3xl">Chest X-ray Scan ML-Based Website</h1>
                            <p className="text-sm text-gray-500 text-light">Welcome to our Chest X-ray Scan ML-Based Website. We utilize cutting-edge machine learning algorithms to assist in the analysis and interpretation of chest X-ray images. Our platform provides accurate and timely results, helping healthcare professionals make informed decisions quickly and efficiently.</p>
                        </div>

                        <Button className="w-48 mt-6 btn-primary poppins" text="Explore Our Services" onClick={() => history('/services')} />
                    </div>
                </Fade>
                <Fade right>
                    <div className="order-1 lg:order-2" style={{ width: '100%', height: '100%' }}>
                        <Lottie animationData={animationData} style={{ width: '100%', height: '100%' }} />
                    </div>
                </Fade>
            </div>
        </section>
    )
}

export default Banner;



